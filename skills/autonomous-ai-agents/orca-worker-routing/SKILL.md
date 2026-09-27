---
name: orca-worker-routing
description: "Use when delegating to Codex/Claude workers via Orca."
---

# Маршрутизация воркеров через Orca

Hermes работает внутри Orca (`TERM_PROGRAM=Orca`, `orca` в PATH). Orca запускает воркеры в
других харнессах с заданной моделью. Проверено 2026-09-23:
`orca orchestration worker-start --agent codex --model gpt-5.6-luna --effort xhigh` → в TUI Codex
виден «GPT-5.6-Luna high»; `--agent claude --model opus --effort high` → Opus 5.5. Полный
контракт: `orca skills get orchestration` (+ `--reference references/coordinator-loop.md`).

## Какой путь выбрать

| Задача | Путь |
|---|---|
| механика без рассуждений (поиск, подсчёт, прогон проверок) | `execute_code` / скрипты, без модели |
| разведка, сводка, правка по готовой спеке | `delegate_task` (Hermes: `delegation.provider: anthropic`, `delegation.model: claude-opus-5-5`, `reasoning_effort: medium`; решение владельца 2026-09-27: Luna xhigh слишком медленная) |
| сложная правка, архитектура, приёмка, спорный баг | Orca-воркер `--agent claude --model opus --effort high` |
| роль с профилем Claude Code (`.claude/agents/*.md`) | Orca-воркер `--agent claude`; в `--spec` путь профиля |
| генерация изображений | координатор сам пишет готовый промпт и принимает; Orca-воркер `--agent codex --model gpt-6-luna --effort xhigh` — **один на картинку, параллельно** (узкое место — `image_gen` ~2 мин/шт., а не модель промпта); новая тема — сначала один целевой арт на одобрение; манифест/контактный лист сводит координатор. В спеке путь к проектному навыку арта (например `.claude/skills/<проект>-art/SKILL.md`, процедура — `docs/studio/ORCA.md`) |

Luna всегда с effort xhigh (решение владельца: почти бесплатна). `gpt-6-sol` и `gpt-6-astra` по умолчанию
не предлагать: по оценке владельца дорогие по токенам и заметного выигрыша не дают.

## Цикл воркера (обязателен)

1. `orca orchestration run-create --objective "..."` → `worker-start --spec ... --worktree current --agent ... --model ... --effort ... --json`.
   Спека: цель, файлы «твои» / «не трогай», ограничения, критерий приёмки, **лимит итераций**
   (глобальное правило 12): «проблема не решилась за 2–3 итерации — не копай: изолируй и опиши
   гипотезу в отчёте либо пришли вопрос». Воркер без лимита копает один баг 30+ минут.
2. **Через 15–20 с после старта проверить, что воркер реально пошёл**:
   `orca orchestration worker-show --dispatch <id> --json` и `orca terminal read --terminal <handle> --screen`.
   Бывает, что Codex получает задание в поле ввода, но не отправляет (`stage: turn_start_unobserved`,
   на экране `draft: "..."` и пустой prompt). Лечение: `orca terminal send --terminal <handle> --enter`,
   затем повторная проверка через 15–20 с. Дубль не запускать, пока не доказано, что первый мёртв.
3. Ждать: `orca orchestration check --wait --types "worker_done,escalation,question" --timeout-ms 900000 --json`.
4. Отчёт воркера — самоотчёт: проверить дифф и прогнать валидацию самому.
5. **Закрыть каждый отработавший воркер**: `check --ack <delivery_id>`, затем
   `orca orchestration worker-release --dispatch <id> --json`. В конце
   `worker-list --run <run_id> --terminal-state reclaimable --json` пуст, в `orca terminal list`
   нет висящих вкладок `worker-*`.

6. **Уведомить владельца** после приёмки, если проект этого требует (это записывается в `CLAUDE.md` проекта):
   `hermes send -t telegram:<OWNER_CHAT_ID> "<роль>: <итог>, <коммит>, <ссылка>"`. Работает без LLM и
   без запущенного шлюза; в ответе `message_id` — доказательство доставки.

## Экономия контекста (глобальное правило 15)

- В спеку каждого воркера вписывать блок: «контекст > ~200 тыс. — закоммить промежуточное, напиши
  `handoff` (сделано / осталось / где лежит / что проверено) в worker_done и остановись; логи через
  фильтр; файлы кусками; разведка кода — субагентом; долгие прогоны — фоном со скриптом-маркером,
  без опроса циклом».
- Новое решение владельца во время работы воркера — не досылать поверх задачи, а записать в файл
  решений и учесть в спеке следующего воркера (досылать только ответ на его вопрос).
- Раздутого воркера (статусбар > 200k) — закрыть после `handoff` и продолжить свежим, спека =
  исходная спека + записка.
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` в `~/.claude/settings.json` → `env` (Claude Code 2.1.x;
  переменная найдена в бинаре, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` — альтернатива в процентах).
  Действует только на новые сессии.

## Ловушки

- `worker-start` → `failed`, `Agent startup blocked: agent-update-prompt`: Codex CLI показал окно обновления. В терминале воркера `orca terminal send --text "3"` + `--enter` («Skip until next version»). Упавшую задачу `--task` не перезапустить (`task_not_startable`), `--retry-of` требует `--spec`: запускать заново `worker-start --spec "$(cat file)" --task-title ...`.
- Claude-воркер в новом каталоге висит на «Do you trust this folder?» (`turn_start_unobserved`). Лечение: в `~/.claude.json` `projects["C:/path/with/forward/slashes"].hasTrustDialogAccepted = true` (бэкап файла перед правкой), закрыть вкладку, запустить новый воркер.
- Вне живой Orca-вкладки (Hermes gateway/Telegram нет `ORCA_TERMINAL_HANDLE`) команды падают `no_active_sender_terminal`. Handle координатора — из `orca terminal list`; `run-create`/`worker-start` принимают `--from <handle>`, а `check` — только `--terminal <handle>` (`--from` там `invalid_argument`).
- Картинки Codex-воркера под Orca лежат в `C:\Users\user\AppData\Roaming\orca\codex-runtime-home\home\generated_images\<session>\exec-*.png` (не `~/.codex`). Владелец хочет видеть каждую сразу: слать `hermes send -t telegram:<OWNER_CHAT_ID> "MEDIA:<path>\n<подпись>"` по мере появления, не ждать `worker_done`; правило стоит записать в `CLAUDE.md` проекта и профиль роли художника. По `worker_done` — карточка решения через `clarify` (варианты «Согласовать»/«Отклонить», Other = отклонить с комментарием; в Telegram рендерится кнопками), одна партия — один `clarify` до 5 вопросов. `hermes send` кнопки не умеет. **`clarify` с `multi_select: true` в Telegram рендерится как выбор одного варианта** — владелец не может отметить несколько (жалоба 2026-09-26). Для партии картинок: по одному вопросу на картинку «Согласовать»/«Отклонить» (до 5 в одном `clarify`, больше — несколькими вызовами подряд) либо один вопрос без choices «перечислите отклонённые, остальные согласую». Ответ владельца reply-ом на картинку иногда приходит без самой картинки — уточнять через `clarify`, не угадывать.
- **claude-mem у Claude-воркеров — чистый расход.** Плагин claude-mem (thedotmack) на каждое событие
  сессии зовёт Haiku; при Hermes-координаторе память ведёт Hermes, и за 5 дней на одной машине вышло
  ~4300 вызовов (~$45). Отключение только для запусков Orca: `agentDefaultEnv.claude.CLAUDE_MEM_INTERNAL = "1"`
  в настройках Orca (новые версии — SQLite `profile-state.db`, старые — `orca-data.json`; правка
  только при закрытой Orca) — пункт 14 `docs/startup-settings.md`
  playbook, скрипт `scripts/orca_agent_env.py`; поля в UI Orca нет. Ручной `claude` в shell-вкладке
  не затронут. Проверка — в воркере `echo $CLAUDE_MEM_INTERNAL` = 1 и 0 строк `sdk_sessions` в
  `~/.claude-mem/claude-mem.db` по папке тестового воркера.
- `check --wait` без `--ack` снова отдаёт ту же непрочитанную пачку; смотреть все сообщения run — `check --all --json`.

- `worker-start --agent codex` вернул `ready`, но `turnStart: unsupported`, а во вкладке — голый PowerShell, в который спека ушла как команды (`Имя "…" не распознано`): Codex не стартовал. Лечение: `worker-release` + `terminal close`, повторить тот же `worker-start` — второй запуск дал `turnStart: observed` (2026-09-26). Признак живого Codex — строка `GPT-6-Luna xhigh · <путь>` и `Working`.
- `worker-release` отзывает dispatch, но **не закрывает вкладку** терминала `worker-*`. После release закрывать явно: `orca terminal close --terminal <handle>`; проверка — `orca terminal list | grep worker`.
- Воркер может прислать `worker_done` повторно уже после release — Orca отклоняет его («capability is revoked»), это не ошибка работы: ack и дальше.
- `check --wait` просыпается и на heartbeat-сообщения в выдаче; смотреть `type`, а не сам факт возврата.
- **`worker-start --worktree current` из Hermes (gateway) открывает Claude-воркер в основном дереве, а не в `cwd` вызова** (статусбар `📁 <проект> | 🌿 master`, 4 из 4 запусков). Первой строкой спеки писать абсолютный путь worktree + «cd туда, git -C для всех git-команд, в основном дереве ничего не менять»; после старта проверить статусбар и при необходимости дослать то же сообщение `orca terminal send`.

- Самоотчёт модели о своём имени и effort недостоверен (Opus назвал effort «low», Codex — «GPT-5»).
  Модель проверять по экрану терминала или по `worker-show` (`effort`).
- `--effort` требует `--model` и несовместим с `--terminal`.
- В `delegate_task` модель одна на всех детей (`delegation.model`); другая модель на одну задачу —
  через Orca-воркер, а не переключением конфига посреди сессии.
