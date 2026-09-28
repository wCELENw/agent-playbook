---
name: orca-worker-routing
description: "Use when dispatching any task to Orca workers (Codex/Claude)."
---

# Маршрутизация и цикл Orca-воркера

Правило и таблица моделей — `GLOBAL_RULES.md` §9 (уже в контексте). Здесь — команды и ловушки.
Полный контракт: `orca skills get orchestration` (+ `--reference references/coordinator-loop.md`).

Координатор не делает модельную работу сам и не зовёт `delegate_task`: владелец прямо поправил
(2026-09-25) — «агенты параллельно» значит отдельные Orca-воркеры, по одному на задачу.

## Выбор флагов

| Задача | Флаги `worker-start` |
|---|---|
| разведка, анализ, сводка, правка по полной спеке | `--agent claude --model opus --effort medium` (`low` для простой разведки) |
| тяжёлая многоэтапная разработка, архитектура, трудная правка, приёмка, спорный баг | `--agent claude --model opus --effort high` (`medium` при полной спеке) |
| роль из `.claude/agents/<role>.md` | `--agent claude --model <model из frontmatter роли> --effort <effort из frontmatter роли>` |
| разовый запрос, поиск в интернете, слив сырой инфы без обработки; изображения | `--agent codex --model gpt-6-luna --effort xhigh` |

Решение владельца 2026-09-28 (заменяет 2026-09-25 и 2026-09-27): Sonnet не используется — разбор,
разведка и сводка на Opus 5.5 medium или low; `delegate_task` не маршрут. Тяжёлая многоэтапная работа
остаётся на Opus 5.5; роли — на модели из своего профиля. Luna только достаёт и сливает,
не анализирует и не правит; всегда effort xhigh (почти бесплатна). `gpt-6-sol` и `gpt-6-astra` по
умолчанию не предлагать: дорогие по токенам без заметного выигрыша. Воркеры пишут в стиле caveman
(в спеке: «отчёт — caveman»); тон Альфреда — только у координатора.

Frontmatter роли (`model`, `effort`, `tools`) в Orca-воркере не действует: effort — флагом,
ограничения инструментов («только чтение» у исследователя и QA) — текстом спеки.

Изображения: координатор сам пишет готовый промпт и принимает; Codex-воркер — **один на картинку,
параллельно** (узкое место — `image_gen` ~2 мин/шт., а не модель промпта); новая тема — сначала
один целевой арт на одобрение; манифест и контактный лист сводит координатор. В спеке путь к
проектному навыку арта (например `.claude/skills/<проект>-art/SKILL.md`).

## Спека (каждая)

Цель; «твои файлы» / «не трогай — у других воркеров»; путь профиля роли, если есть; числа, id и
`файл:строка` прямо в тексте; «не коммитить, не пушить, не деплоить»; запуск инструментов проекта;
путь отчёта и «писать раздел за разделом»; критерий приёмки (команда и ожидаемый вывод);
**лимит итераций** (глобальное правило 12): «проблема не решилась за 2–3 итерации — не копай:
изолируй и опиши гипотезу в отчёте либо пришли вопрос» — воркер без лимита копает один баг 30+ минут.
Спеку класть файлом в scratch и передавать `--spec <путь>`.

## Цикл

0. Перед выдачей: `orca orchestration task-list --brief` и `git worktree list` — сверить scope новой
   задачи с активными задачами и неслитыми ветками; уже выданное повторно не выдавать
   (идея из studioigor/gamestudio `STUDIO.md:298-302`).
1. `orca orchestration run-create --objective "..." --json` — один Run на волну.
2. `worker-start --run <run> --spec "..." --worktree current --agent ... --model ... --effort ... --json` —
   всю независимую волну до первого ожидания.
3. Через 15–20 с: `worker-show --dispatch <id> --json` → `launch.effective` совпадает с запрошенным;
   `orca terminal read --terminal <handle> --screen` — агент работает. Codex иногда оставляет
   задание в поле ввода (`turn_start_unobserved`, на экране `draft: "..."`): `orca terminal send
   --terminal <handle> --enter`, проверить ещё раз. Стадия может остаться
   `turn_start_unobserved` и после Enter — смотреть экран («Working»). Дубль не запускать без
   доказательства смерти первого.
4. `check --wait --types "worker_done,escalation,question" --timeout-ms <ms> --json`.
   Вопрос воркера — `reply --id <message_id>`; решение владельца для работающих воркеров —
   `orca orchestration send --to dispatch:<id> --subject ... --body ...`.
5. `worker_done` — самоотчёт: `git status --short` (ровно ожидаемые файлы), дифф, гейты проекта.
6. Судьба терминала до ack: следующая задача тому же агенту —
   `worker-start --task <новая> --terminal <handle>`; иначе `worker-release --dispatch <id>`.
   Затем `check --ack <delivery_id>`.
7. Конец волны: `worker-list --run <run_id> --terminal-state reclaimable --json` пуст;
   `worker-list --json` → `counts.retained` не растёт без решения владельца; в `orca terminal list`
   нет висящих вкладок `worker-*`.
8. Коммит — координатор, явными путями из `--files-modified` после проверки диффа (`git add <пути>`,
   не `git add -A`: соседний воркер в том же worktree может ещё писать).
9. **Уведомить владельца** после приёмки, если проект этого требует (записано в `CLAUDE.md` проекта):
   `hermes send -t telegram:<OWNER_CHAT_ID> "<роль>: <итог>, <коммит>, <ссылка>"`. Работает без LLM и
   без запущенного шлюза; в ответе `message_id` — доказательство доставки.

## Экономия контекста (глобальное правило 15)

- В спеку каждого воркера вписывать блок: «контекст > ~200 тыс. — закоммить промежуточное, напиши
  `handoff` (сделано / осталось / где лежит / что проверено) в worker_done и остановись; логи через
  фильтр; файлы кусками; долгие прогоны — фоном со скриптом-маркером, без опроса циклом».
- Новое решение владельца во время работы воркера — не досылать поверх задачи, а записать в файл
  решений и учесть в спеке следующего воркера (досылать только ответ на его вопрос).
- Раздутого воркера (статусбар > 200k) — закрыть после `handoff` и продолжить свежим, спека =
  исходная спека + записка.
- `CLAUDE_CODE_AUTO_COMPACT_WINDOW=300000` в `~/.claude/settings.json` → `env` (Claude Code 2.1.x;
  `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` — альтернатива в процентах). Действует только на новые сессии.

## Ловушки

- Новая папка: Claude спрашивает «trust this folder» — до запуска добавить
  `projects["C:/путь"].hasTrustDialogAccepted=true` в `~/.claude.json` (бэкап перед правкой); Codex — `trust_level` в config.toml.
  Codex после установки плагинов спрашивает про хуки — один раз запустить `codex` в терминале и выбрать «Trust all».
  Иначе preamble улетает в PowerShell как команды.
- `worker-start` → `failed`, `Agent startup blocked: agent-update-prompt`: Codex CLI показал окно обновления.
  В терминале воркера `orca terminal send --text "3"` + `--enter` («Skip until next version»). Упавшую задачу
  `--task` не перезапустить (`task_not_startable`), `--retry-of` требует `--spec`: запускать заново
  `worker-start --spec "$(cat file)" --task-title ...`.
- Вне Orca-терминала (Hermes gateway/Telegram, нет `ORCA_TERMINAL_HANDLE`) команды падают
  `no_active_sender_terminal`. Координатору нужен свой терминал: `orca repo add --path`,
  `orca terminal create --worktree path:... --json` (или handle из `orca terminal list`); handle — `--from`
  у run-create/worker-start/send и `--terminal` у check (`--from` там `invalid_argument`).
- **`worker-start --worktree current` из Hermes gateway открывает Claude-воркер в основном дереве, а не в `cwd`
  вызова.** Первой строкой спеки писать абсолютный путь worktree + «cd туда, git -C для всех git-команд, в основном
  дереве ничего не менять»; после старта проверить статусбар.
- Codex иногда стартует пустым (`turn_start_unobserved`, поле ввода пустое >60 с) или голым PowerShell, в который
  спека ушла как команды (`turnStart: unsupported`, `Имя "…" не распознано`) — release/abandon + `terminal close` +
  тот же `worker-start` заново; несколько Codex подряд запускать с паузой ~20 с. Признак живого Codex —
  строка `GPT-6-Luna xhigh · <путь>` и `Working`.
- Упавший воркер «возобновляется» новой задачей в тот же терминал (шаг 6), а не новым воркером;
  перед этим закоммитить то, что он успел записать.
- `check --json` печатает несколько JSON подряд — разбирать `json.JSONDecoder().raw_decode` в цикле;
  тип — `type`, текст — `body`, `dispatchId` — в JSON-строке `payload`, id доставки — `result.deliveryId`.
- `check --wait` просыпается на heartbeat — смотреть `type`. Без `--ack` он снова отдаёт ту же
  непрочитанную пачку; все сообщения run — `check --all --json`.
- Долгое ожидание — в `terminal` (timeout до 600 с), а не в `execute_code`: ячейка убивается
  через 300 с вместе со состоянием. Разбор и ack — скриптом в scratch, который дописывает
  результаты в json-файл (состояние переживает таймаут).
- Длинный inline-цикл bash с `$(...)` Hermes блокирует как «malformed payload» — вынести в скрипт.
- `worker_done` после release отклоняется («capability is revoked») — это не ошибка, ack.
- `--effort` требует `--model` и несовместим с `--terminal`.
- Самоотчёт модели о себе недостоверен; модель — только `launch.effective` или экран терминала.
- `orca terminal close` не заменяет `worker-release`, а `worker-release` не закрывает вкладку. Если после
  release вкладка осталась (`orca terminal list`), закрыть её `orca terminal close --terminal <handle>` —
  только после release и только для этого handle.
- Роль с профилем `.claude/agents/*.md` — только Orca-воркер `--agent claude`; субагент внутри
  Hermes (`delegate_task`) ролью не считается.
- Картинки Codex-воркера под Orca лежат в `C:\Users\user\AppData\Roaming\orca\codex-runtime-home\home\generated_images\<session>\exec-*.png`
  (не `~/.codex`). Владелец хочет видеть каждую сразу: слать `hermes send -t telegram:<OWNER_CHAT_ID> "MEDIA:<path>\n<подпись>"`
  по мере появления, не ждать `worker_done`. По `worker_done` — карточка решения через `clarify`
  («Согласовать»/«Отклонить», Other = отклонить с комментарием; в Telegram — кнопки), до 5 вопросов в одном `clarify`.
  `hermes send` кнопки не умеет. **`clarify` с `multi_select: true` в Telegram рендерится как выбор одного
  варианта** — для партии картинок по одному вопросу на картинку либо один вопрос без choices «перечислите
  отклонённые». Ответ reply-ом на картинку иногда приходит без самой картинки — уточнять, не угадывать.
- **claude-mem у Claude-воркеров — чистый расход.** Плагин claude-mem (thedotmack) на каждое событие
  сессии зовёт Haiku; при Hermes-координаторе память ведёт Hermes, и за 5 дней на одной машине вышло
  ~4300 вызовов (~$45). Отключение только для запусков Orca: `agentDefaultEnv.claude.CLAUDE_MEM_INTERNAL = "1"`
  в настройках Orca (новые версии — SQLite `profile-state.db`, старые — `orca-data.json`; правка
  только при закрытой Orca) — пункт 14 `docs/startup-settings.md` playbook, скрипт
  `scripts/orca_agent_env.py`; поля в UI Orca нет. Ручной `claude` в shell-вкладке не затронут.
  Проверка — в воркере `echo $CLAUDE_MEM_INTERNAL` = 1 и 0 строк `sdk_sessions` в
  `~/.claude-mem/claude-mem.db` по папке тестового воркера.
