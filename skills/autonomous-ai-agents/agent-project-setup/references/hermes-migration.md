# Перенос настроек Hermes на другой ПК

Цель: визуал, конфиг, SOUL, память, навыки, плагины — без секретов и без истории.

## Что брать (из `$HERMES_HOME`)

| Файл/каталог | Что в нём |
|---|---|
| `config.yaml` | модели, effort, делегирование, `display.*` (скин, details_mode, звук). Ключей нет — только `key_env` |
| `SOUL.md` | обычно symlink на `~/.agents/GLOBAL_RULES.md` — класть **содержимое цели**, не ссылку |
| `memories/MEMORY.md`, `memories/USER.md` | память (без `*.lock`) |
| `assets/` | аватар |
| `skills/` | все навыки, включая `.hub`, `.curator_*`, `.bundled_manifest` |
| `plugins/` | плагины (без `__pycache__`) |
| `skins/`, `tui-widgets/`, `pets/`, `desktop-plugins/`, `hooks/` | если непустые |

Не брать: `.env`, `auth.json` (секреты — на новом ПК заново `hermes model`/`hermes auth`);
`state.db*` (история, десятки МБ); кэши (`cache/`, `models_dev_cache.json`, `tui-theme-boot.json`
— пересоздаются из скина); `hermes-agent/`, `node/`, `bin/`.

## Сборка

`hermes backup` не подходит для переноса «без секретов»: полный режим берёт `.env`, `auth.json`
и `state.db`, а symlink'и (SOUL.md) пропускает. Собирать zip в `execute_code` (stdlib `zipfile`):
`os.walk` по `skills`/`plugins`, пропуск `__pycache__`, `.locks`, `*.lock`, `*.pyc`, symlink'ов;
`SOUL.md` писать из пути цели. Проверки после записи: `testzip() is None`, в `namelist()` нет
`.env`/`auth.json`, список верхнего уровня.

Выход — в `~` (`C:\Users\<user>\hermes-migration-<дата>.zip`), путь отдать владельцу текстом.

## Восстановление на новом ПК

1. Установить Hermes.
2. `hermes import <zip>` — импорт принимает архив, если в нём есть `config.yaml`.
3. Вход в провайдеры заново; ключи из `.env` вручную.
4. Symlink'и воссоздать (`SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` → `~/.agents/GLOBAL_RULES.md`),
   иначе правила разойдутся; конфиги Claude Code (`~/.claude`) и Codex (`~/.codex`) — отдельный перенос.

В отчёте владельцу: что вошло, что исключено и почему, три шага восстановления.
