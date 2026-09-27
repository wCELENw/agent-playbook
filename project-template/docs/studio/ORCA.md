# Запуск воркеров через Orca — для Producer

Полный цикл и ловушки — навык `orca-worker-routing`; спеки и приёмка — `agent-delegation-and-verification`.

## Запуск

```
orca orchestration run-create --objective "<итерация>"
orca orchestration task-create --spec "$(cat <файл спеки>)" --task-title "<роль: пачка>" --json
orca orchestration worker-start --task <ПОЛНЫЙ id> --worktree <дерево> \
  --agent <agent роли> --model <model роли> --effort <effort роли> --json
```

- `agent`, `model`, `effort` — из frontmatter `.claude/agents/<роль>.md`; строка
  `model: …, effort: …` в карточке переопределяет роль.
- В спеке: первой строкой `ДЕРЕВО: <абсолютный путь worktree>`, путь профиля роли,
  `docs/studio/common.md`, глагол действия, ветка и фраза «работа не сделана, если своих коммитов
  нет». Ссылка «прочитай план» без глагола исполняется как пересказ.
- Тело спеки — из файла через `$(cat …)`: обратные кавычки в двойных кавычках шелл выполняет.
- Параллельным воркерам с docker — свой `COMPOSE_PROJECT_NAME`.

## Первые минуты

- Через 15–20 с проверить, что воркер пошёл (`worker-show`, `orca terminal read --screen`).
  Спека стоит в поле ввода — `orca terminal send --terminal <h> --enter`. Дубль не запускать,
  пока не доказано, что первый мёртв.
- Живой claude: `⏺`, `esc to interrupt`; codex: `Working`.
- Codex `agent-update-prompt` — в терминале «3. Skip until next version» + Enter; упавшую задачу
  запускать заново через `worker-start --spec "$(cat …)" --task-title …`.
- Claude «Do you trust this folder?» — `hasTrustDialogAccepted: true` в `~/.claude.json` для проекта.

## Приёмка

- «Готово» ≠ «закоммичено»: `git -C <дерево> status --short` пуст, вершина — коммит воркера.
- `git merge master` в ветку задачи, ворота там же, потом мерж в master; маркеров конфликтов — 0.
- Вопрос воркера — `orchestration reply --id <msg>` + дубль `orca terminal send "Ответ Producer: …"`.
- Красную приёмку возвращать тому же живому воркеру; освобождать только после своей приёмки.
- После приёмки: `worker-release`, `orca terminal close`, убить серверы дерева.
- Уведомить владельца одной строкой: `hermes send -t telegram:<chat_id> "<роль>: <итог>, <коммит>, <ссылка>"`.

## Изображения

Промпт пишет Producer; генерирует Codex-воркер — один на картинку, параллельно. Новая тема — сначала
один целевой арт на одобрение. Воркер шлёт каждую картинку владельцу сразу; по `worker_done`
Producer присылает `clarify` «Согласовать / Отклонить» (Other = отклонить с комментарием).
Подробно — `agent-delegation-and-verification/references/image-batch-acceptance.md`.
