---
name: agent-project-setup
description: "Use when wiring Hermes/Codex/Claude or adding skill packs."
---

# Настройка харнессов (Hermes, Claude Code, Codex) без дублей

Класс задач: аудит или первичная настройка агентов под проект, маршрутизация моделей,
экономия токенов, единые правила для всех харнессов. Владелец хочет минимум токенов,
атомарные задачи и разделение обязанностей; один источник истины на каждый факт.

## Целевая схема (один файл — один источник)

| Что | Канон | Как доставляется в харнессы |
|---|---|---|
| глобальные правила (тон, язык, формат, маршрутизация) | `~/.agents/GLOBAL_RULES.md` | symlink'и: `$HERMES_HOME/SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` |
| правила проекта | `<repo>/CLAUDE.md` | Hermes и Claude Code грузят сами; Codex — `project_doc_fallback_filenames = ["CLAUDE.md"]` в config.toml |
| навыки проекта | `<repo>/.claude/skills/<name>/SKILL.md` | `<repo>/.agents/skills` → symlink на `.claude/skills` (его читают Hermes и Codex); Hermes: `hermes skills trust` в корне |
| роли | `<repo>/.claude/agents/*.md` | Claude Code напрямую; остальным — путь профиля в спеке воркера |

Запрещено и почему:
- `AGENTS.md` «прочитай CLAUDE.md» рядом с `CLAUDE.md` — Hermes берёт AGENTS.md раньше CLAUDE.md
  (first match wins), и каждая сессия тратит вызов и весь файл на повторное чтение.
- Копии проектных навыков в `$HERMES_HOME/skills/` — копии расходятся: факты пишутся в одну,
  читается другая. Перед удалением копии слить уникальные строки в канон
  (`diff --strip-trailing-cr canon copy | grep '^>'`) — именно там бывают свежие ловушки.
- Адаптеры ролей для других харнессов (`.codex/agents/*`), которые лишь ссылаются на профиль.

## Чек-лист нового проекта

Основа — `~/.agents/GLOBAL_RULES.md` §9 (маршрутизация моделей) и §10 (раскладка проекта).

1. `CLAUDE.md` в корне репо — единственный свод правил проекта; `AGENTS.md` не создавать.
2. Навыки — `.claude/skills/<name>/SKILL.md`, роли — `.claude/agents/*.md`; `description` во
   frontmatter в кавычках.
3. Symlink навыков из git-bash: `MSYS=winsymlinks:nativestrict ln -s ../.claude/skills .agents/skills`
   (проверка: `git ls-files -s .agents/skills` → mode `120000`).
4. Hermes: `hermes skills trust <path>` в корне репо.
5. Codex: проект в trusted (`[projects.'<path>'] trust_level = "trusted"` в `~/.codex/config.toml`
   и в Orca-копии config.toml); `project_doc_fallback_filenames = ["CLAUDE.md"]` — первой строкой
   верхнего уровня в ОБОИХ config.toml. Проверять наличие, а не считать установленным: Codex/Orca
   переписывают config.toml, и строка пропадает (2026-09-24 её не было ни в одном). Проверка —
   `codex debug prompt-input hi` из репо и grep по фразе из CLAUDE.md, для каждого дома.
5a. Claude Code: для воркеров Orca проект должен быть доверенным — `hasTrustDialogAccepted: true`
   в `~/.claude.json` → `projects["C:/..."]`, иначе воркер висит на диалоге доверия.
5b. Сторонние навыки (пакеты вроде awesome-gamedev-agent-skills) — вендорить в `.claude/skills/`
   только нужные (по движку и ролям), лицензию и NOTICE — в `docs/third-party/`; не ставить весь
   пакет через `npx skills add`/плагин: индекс навыков стоит токенов в каждом запросе.
6. Никаких копий проектных навыков в `$HERMES_HOME/skills/`, `~/.codex/skills` и т.п.
7. Проверка загрузки: Hermes — `hermes chat -q "list project skills" -Q` из репо (навыки с меткой
   `[project]`, без дублей) или `skills_list`; Codex — `codex exec -s read-only "первая строка CLAUDE.md?"`
   отвечает дословно.

## Порядок аудита / настройки

1. **Инвентаризация** (без модели, одним вызовом): `hermes config show`, нужные секции
   `$HERMES_HOME/config.yaml` (без секретов), `~/.codex/config.toml`, `~/.claude/settings.json`,
   `<repo>/{CLAUDE.md,AGENTS.md,.claude,.codex,.agents}`, `hermes auth list`, `env | grep ORCA`.
   Под Orca у Codex свой `CODEX_HOME` (`%APPDATA%\orca\codex-runtime-home\home`) — править
   config.toml в ОБОИХ местах, иначе воркеры Orca идут со старыми настройками.
2. **Резервные копии** в `$HERMES_HOME/backups/` перед любой правкой глобальных файлов.
3. **Модели** — см. `references/harness-config.md` (ключи, проверки и порядок смены модели
   во всех местах). Маршрутизация задач по моделям и цикл Orca-воркера — скилл `orca-worker-routing`.
4. **Симлинки на Windows**: `pwsh -NoProfile -Command "New-Item -ItemType SymbolicLink -Path <link> -Target <file>"`
   (работает без админа при включённом Developer Mode; для каталога можно `-ItemType Junction`).
   `cmd //c mklink` из git-bash молча не срабатывает. Сканер навыков Hermes ходит по ссылкам
   (`os.walk(followlinks=True)`).
5. **Индекс навыков** в системном промпте стоит токены в КАЖДОМ запросе: ненужные группы
   выключать списком имён в `skills.disabled` (матчится по имени навыка, не по категории;
   категорию раскрыть в имена через `name:` во frontmatter).
6. **Проверка каждой настройки реальным вызовом**, не по файлу:
   `hermes chat -q "Reply with exactly: OK" -Q` (+ `--provider X -m Y`) и строка `API call #1: model=... provider=...`
   в `$HERMES_HOME/logs/agent.log`; Codex — `codex exec --skip-git-repo-check -s read-only "<вопрос про первую
   строку CLAUDE.md и слово из глобальных правил>"`.
7. **Сторонние пакеты навыков/плагинов** (caveman, ponytail и т.п.) — порядок установки, сканер,
   ручная установка плагина, проверка загрузки и включение режима по умолчанию во всех трёх
   харнессах (auto_load / хуки / `developer_instructions`): `references/third-party-skill-packs.md`.
8. Коммит в репозитории — только изменения схемы (симлинк `.agents/skills`, удаление дублей,
   правка CLAUDE.md); глобальные файлы в репо не попадают.

## Вывод владельцу

По-русски, только ключевые выводы по этапам (сделано / чем подтверждено / что осталось);
детализацию не выносить. В финале аудита — таблица «решение/роль → харнесс → модель → effort».
Предложения владельца по моделям не оспаривать повторно после его решения (пример: Luna —
всегда effort high, она почти бесплатна).

## Ловушки

- **Модели «нет» в `codex debug models` — сначала обновить CLI и кэш, потом говорить владельцу.**
  Старый Codex CLI (0.151) и `models_cache.json` не показывали gpt-6-*; помогло
  `npm install -g @openai/codex@latest` + переименование `models_cache.json` в ОБОИХ домах
  (`~/.codex`, `%APPDATA%\orca\codex-runtime-home\home`). Проверка — `codex exec -m <slug> "Reply OK"`.
- **Доступность модели проверять живым каталогом, а не кэшем**: `codex debug models` (slug +
  уровни effort). `~/.codex/models_cache.json` и список `providers.*.models` в Hermes config.yaml
  отстают от обновлений — по ним новая модель «не существует», и владельцу задаётся лишний вопрос.
  Имя со слов владельца («luna 6») сопоставлять со slug из каталога (`gpt-6-luna`).

- **Длинная сессия на Anthropic может обрываться `finish_reason=content_filter` (refusal)** —
  в интерфейсе это выглядит как «что-то встало». Первым делом `tail $HERMES_HOME/logs/errors.log`,
  затем проверить побочные эффекты (`git status`, `delegate_task action=list`, `orca terminal list`).
  После второго обрыва предложить новую сессию с кратким списком оставшегося.
- **`hermes config set` на часть рабочих ключей пишет «not a recognized config key»**
  (`agent.reasoning_effort`, `delegation.reasoning_effort`, `display.details_mode`, `display.sections.*`).
  Предупреждение ≠ ошибка: проверять чтение ключа grep'ом по исходникам
  `$HERMES_HOME/hermes-agent` (`hermes_constants.py`, `tools/delegate_tool_config.py`, `ui-tui/src`).
- **Смена `model.provider` не сбрасывает `model.base_url`/`api_mode`/`key_env`** от прежнего провайдера —
  запросы уйдут на старый endpoint. Сразу `hermes config unset` всех трёх.
- **Файловые пути для нативных программ** (py, codex) из git-bash: `$TMPDIR` раскрывается в `/tmp`,
  который нативные программы не видят; писать в `$LOCALAPPDATA/Temp` и передавать `C:/...`.
- **Описание навыка/роли во frontmatter — всегда в кавычках**: `: ` внутри строки ломает YAML,
  и навык молча пропадает. Проверка всех разом — `yaml.safe_load` блока между `---`.
- Поле `model:` во frontmatter `.claude/agents/*.md` читает только Claude Code; Hermes и Codex его
  игнорируют — для них модель задаётся конфигом или `worker-start --model`.
