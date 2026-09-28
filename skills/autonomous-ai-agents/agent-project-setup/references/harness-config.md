# Ключи настройки харнессов (проверены реальным вызовом)

## Hermes (`hermes config set KEY VAL`; config.yaml руками не править)

| Цель | Ключи |
|---|---|
| основная модель (координатор) | `model.provider anthropic`, `model.default claude-opus-5-5`; старые `model.base_url/api_mode/key_env` — `unset` |
| effort основной модели | `agent.reasoning_effort high` (пер-модельно: `agent.reasoning_overrides`) |
| подагенты `delegate_task` (не маршрут по §9 — только если владелец назвал его явно) | `delegation.provider anthropic`, `delegation.model claude-opus-5-5`, `delegation.reasoning_effort medium` |
| служебные вызовы на дешёвую модель | `auxiliary.{compression,title_generation,approval,skills_hub}.{provider,model}` |
| ревью `/review` на сильную модель | `auxiliary.review.provider anthropic`, `auxiliary.review.model claude-opus-5-5` |
| звук при вопросе к владельцу | `display.bell_on_prompt true` |
| рассуждения/инструменты свёрнуты (как в Claude) | `display.details_mode collapsed`, `display.sections.{thinking,tools,subagents} collapsed`, `display.show_commentary false`; в сессии — `/details collapsed` |
| навыки проекта | `hermes skills trust` в корне репо (читает `.hermes/skills`, `.agents/skills`) |

В `delegate_task` модель одна на всех детей; другая модель на задачу — Orca-воркер, а не переключение
конфига посреди сессии. Изменения конфига и SOUL.md действуют с СЛЕДУЮЩЕЙ сессии —
текущая системный промпт не перечитывает (кэш промпта).

## Codex (`~/.codex/config.toml` И `%APPDATA%\orca\codex-runtime-home\home\config.toml`)

```toml
model = "gpt-6-luna"
model_reasoning_effort = "xhigh"
project_doc_fallback_filenames = ["CLAUDE.md"]
```

## Claude Code (`~/.claude/settings.json`)

- `model` + `modelSettings.<model>.effortLevel` — модель и effort по умолчанию.
- Звук: `hooks.Notification = [{matcher:"", hooks:[{type:"command", command:"powershell -NoProfile -Command \"[System.Media.SystemSounds]::Asterisk.Play()\""}]}]`.
  Править JSON скриптом (load → setdefault → dump), не затирая чужие хуки (Orca, claude-mem).

## Смена модели во всех местах (например, «переключи Luna на новую версию»)

1. **Каталог**: `codex debug models` → нужный slug и поддерживает ли он запрошенный effort.
2. **Найти все вхождения старого slug** одним grep: `$HERMES_HOME/config.yaml`
   (`delegation.model`, `auxiliary.*.model`), `~/.codex/config.toml`, Orca-копия config.toml,
   `~/.agents/GLOBAL_RULES.md` (таблица §9), `<repo>/.claude/skills/**` и `.claude/agents/*.md`
   (спеки воркеров `--model`), этот файл.
3. **Заменять только выбор модели**. Не трогать: `providers.<name>.models` (перечень доступного,
   не выбор), суффиксные варианты (`-pro`), исторические отчёты `docs/qa/*` (снимок на дату).
   sed с границей: `s/OLD\b\([^-]\|$\)/NEW\1/g`, затем вернуть строки провайдерского списка.
4. **Бэкап** перед правкой (`$TMPDIR` или `$HERMES_HOME/backups/`), после — парс `yaml.safe_load` /
   `tomllib.load` каждого конфига.
5. **Живая проверка**: `codex exec --skip-git-repo-check "Reply with exactly: OK"` (в выводе
   `model: <slug>`) и `hermes -z "Reply with exactly: OK" -m <slug> --provider openai-codex`.
6. Коммит в репо — только проектные файлы (скиллы/роли); глобальные конфиги не коммитятся.
   Владельцу сказать, что текущая сессия подхватит новый конфиг только после перезапуска.

## Смена effort во всех местах (например, «xhigh → high для Opus»)

1. Один grep по `effort` во всех местах: `.claude/agents/*.md` (frontmatter `effort:`), `<repo>/CLAUDE.md`
   (текстовое описание раскладки), `.claude/skills/**`, `~/.agents/GLOBAL_RULES.md` §9,
   `$HERMES_HOME/config.yaml` (`agent.reasoning_effort`, `delegation.reasoning_effort`),
   `~/.codex/config.toml` + Orca-копия, `~/.claude/settings.json` (`effortLevel`).
2. **Фильтр по модели**: менять только там, где effort относится к названной модели. В ролях —
   `grep -l "effort: xhigh" | xargs grep -H "^model:"`; Luna/Codex-строки с тем же уровнем не трогать
   и перечислить владельцу как оставленные намеренно. Исторические `docs/qa/*` не править.
3. Править только совпавшие файлы (`grep -l … | xargs sed -i`), а не весь glob; проверить CRLF
   (см. ловушку ниже), `git diff --stat` — ровно по строке на файл. Коммит проектных файлов.

**Ловушка CRLF**: `sed -i` в git-bash переписывает CRLF-файл с LF-окончаниями даже там, где
замены не было, — дифф раздувается на весь файл. После правки: `file <f>` (должно быть
`with CRLF line terminators`); затронутые без изменений — `git checkout --`, остальные —
`perl -pi -e 's/\r?\n/\r\n/'`.
