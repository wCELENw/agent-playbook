# agent-playbook

**[English](#english) · [Русский](#русский)**

---

## English

A playbook for running AI coding agents across projects: global rules, model routing, delegation to
Orca workers, acceptance of their work, and **visualising the work in the
browser**: live dashboards for long runs, analytical report pages with charts, and clickable
prototypes and diagrams. The owner sees what the agents are doing and what they produced without
reading raw logs. Distilled from hands-on work across dozens of projects.

Harnesses: [Hermes Agent](https://hermes-agent.nousresearch.com), Claude Code, Codex.

**Main scenario.** The playbook is tuned for one setup: Hermes is the coordinator you talk to
(desktop app, CLI or Telegram), and it launches Claude Code and Codex workers in Orca, each in its
own terminal and git worktree. Hermes plans, routes, reviews and commits; Orca workers do the heavy
edits in parallel. The rules and skills also work in plain Claude Code or Codex, but the delegation,
worker lifecycle and acceptance parts assume Hermes + Orca.

### How it works

![How a task flows through the agents](docs/how-it-works.en.png)

The owner sets a task. The coordinator (Hermes on Claude Opus 5.5) breaks it down and picks an executor
from the routing table in `global/GLOBAL_RULES.md` §9:

| Work | Executor |
|---|---|
| mechanical, read-only: search, counting, git, running checks | the coordinator itself, no model |
| recon, analysis, aggregation, edits from a complete spec | Orca worker, Claude Opus 5.5 medium (low for simple recon) |
| heavy multi-stage development, architecture, hard edits, acceptance review, hard bugs | Orca worker, Claude Opus 5.5 high (medium when the spec is complete) |
| a role with a profile in `.claude/agents/*.md` | Orca worker with the model and effort from that profile |
| one-off lookup, web search, raw info dump; image generation | Orca worker, Codex `gpt-6-luna` xhigh |

Every task that needs a model goes to its own Orca worker (one worker, one task, one set of files);
the coordinator does not write project files itself. Hermes `delegate_task` and in-session subagents
are not routes. Sonnet is not used (owner decision 2026-09-28); Luna only fetches and dumps.

A worker's report is a self-report, not a fact. The coordinator checks the diff and runs the project's
validation, then commits and reports back with `file:line` evidence. Anything the owner should look
at goes to a web page: a live monitor of simulation runs, an analytical report with charts and
decision cards, or a playable UI prototype. The page is served inside a private network (Tailscale
tailnet) and is checked for HTTP 200 and with a headless-browser screenshot before the link is sent.
If a problem is not solved in 2–3 iterations, the agent parks it or brings it to the owner (§12).

Interactive diagram (search, focus, relationship tracing, export): download
`docs/how-it-works.en.html` and open it in a browser. Source: `docs/how-it-works.en.workflow.json`,
built with [Archify](https://github.com/tt-a1i/archify).

### Contents

| Path | What | Installed to |
|---|---|---|
| `global/GLOBAL_RULES.md` | global rules: principles, language and tone, model routing (§9), project layout (§10), always-on skills (§11), iteration cap (§12), CPU cap (§13), results as web pages (§14), worker context economy (§15) | `~/.agents/GLOBAL_RULES.md` + symlinks from `%LOCALAPPDATA%\hermes\SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` |
| `skills/<category>/<name>` | global Hermes skills | `%LOCALAPPDATA%\hermes\skills\` |
| `project-template/` | skeleton of a new project: `CLAUDE.md`, studio process, roles, task queue | root of a new repository |
| `docs/startup-settings.md` | machine checklist for Hermes + Orca: each setting with its check | run by your agent after install |

Key skills: `agent-delegation-and-verification` (spec, self-report check, acceptance),
`orca-worker-routing` (Codex/Claude workers via Orca), `agent-cost-monitoring` (token cost vs
estimate), `browser-page-preview` (dashboards, reports and prototypes as web pages),
`agent-project-setup` and `agent-harness-config` (one set of rules and skills for all harnesses),
`game-*` (preproduction, balance simulations, UI prototypes). The skills and rules are written in
Russian; the commands, paths and code in them are language-neutral.

### Before you use it

This is a personal working configuration published as an example. Replace the placeholders
`<OWNER_CHAT_ID>` and `<tailnet>`, the machine names (`minipc`, `powerpc-1`), the `C:\Users\user\…`
paths and the CPU limits with your own. No secrets are stored here: bot tokens and API keys live in
each project's `.env`.

### Install with your agent (easiest)

Paste this into Hermes, Claude Code or Codex on the target machine:

```text
Install the agent playbook from https://github.com/wCELENw/agent-playbook on this machine.
Follow its README "Install manually" steps and skills/autonomous-ai-agents/agent-project-setup/SKILL.md.
Before copying, show me which of my existing rules and skills would be overwritten and wait for my OK.
Ask me for the values behind the placeholders (<OWNER_CHAT_ID>, <tailnet>, machine names,
paths, CPU limits) and put them into the installed copies only, never into the clone.
Record the installed commit in ~/.agents/agent-playbook.version.
Finish by checking that each harness actually loads the rules and skills.
Then read docs/startup-settings.md and carry out every item, reporting each check's result.
```

The agent reads the repo, adapts it to your machine and asks before overwriting anything.

### Install manually (Windows, git-bash)

```bash
git clone https://github.com/wCELENw/agent-playbook ~/agent-playbook
mkdir -p ~/.agents && cp ~/agent-playbook/global/GLOBAL_RULES.md ~/.agents/GLOBAL_RULES.md
# symlinks (Developer Mode): SOUL.md, ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md -> ~/.agents/GLOBAL_RULES.md
cp -r ~/agent-playbook/skills/* "$LOCALAPPDATA/hermes/skills/"
git -C ~/agent-playbook rev-parse HEAD > ~/.agents/agent-playbook.version
# early auto-compaction for Claude Code (rule 15): env in ~/.claude/settings.json
python -c "import json,pathlib;p=pathlib.Path.home()/'.claude/settings.json';d=json.loads(p.read_text('utf-8')) if p.exists() else {};d.setdefault('env',{})['CLAUDE_CODE_AUTO_COMPACT_WINDOW']='300000';p.write_text(json.dumps(d,indent=2,ensure_ascii=False),'utf-8')"
```

Then replace the placeholders in the installed copies.

**Last step, required:** ask your agent "Read docs/startup-settings.md in ~/agent-playbook and carry
out every item, reporting each check." It sets up the machine-level settings the Hermes + Orca
workflow relies on (models, trust dialogs, sound, claude-mem off for workers, Orca env). Without it
workers can hang or burn tokens.

Full steps, including the load check for each
harness: `skills/autonomous-ai-agents/agent-project-setup/SKILL.md`. On macOS/Linux use
`~/.hermes/skills` instead of `$LOCALAPPDATA/hermes/skills`.

### New project

1. Copy `project-template/` into the repository root and fill in `CLAUDE.md`.
2. Add project roles as `.claude/agents/<role>.md`, modelled on `architect`/`doc-keeper`/`qa-tester`
   (model and effort in the frontmatter); list their zones in `docs/studio/STUDIO.md` §2.
3. `MSYS=winsymlinks:nativestrict ln -s ../.claude/skills .agents/skills`, then `hermes skills trust .`.

### Staying up to date

Your installed copies are personalised, so an update is a merge, not a blind copy. Ask your agent:

```text
Update the agent playbook: git pull in ~/agent-playbook, then summarise what changed since the commit
in ~/.agents/agent-playbook.version. Merge the changes into my installed rules and skills, keeping my
own values and local edits; ask me where they conflict. Update the version file and re-run the
load check.
```

Manual equivalent:

```bash
cd ~/agent-playbook && git pull
git log --oneline "$(cat ~/.agents/agent-playbook.version)..HEAD"      # what is new
git diff "$(cat ~/.agents/agent-playbook.version)..HEAD" -- global skills  # merge these by hand
git rev-parse HEAD > ~/.agents/agent-playbook.version
```

To check regularly, either click **Watch** on GitHub, or let Hermes do it on a schedule, e.g.
`/cron add "0 10 * * 1" "Check github.com/wCELENw/agent-playbook for commits newer than
~/.agents/agent-playbook.version and send me a short summary; do not install anything."`

### License

[MIT](LICENSE). Third-party skill packs (`caveman`, `ponytail`, `archify`, Orca `orchestration`) are
not included and are distributed under their own licenses.

---

## Русский

Шаблон поведения агентов для всех проектов: глобальные правила, маршрутизация моделей, делегирование
воркерам Orca, приёмка их работы и **визуализация работы в браузере**: живые
дашборды долгих прогонов, аналитические страницы отчётов с графиками, кликабельные прототипы и схемы.
Владелец видит, что делают агенты и что получилось, не читая сырые логи. Собран на базе работы
над десятками проектов.

**Основной сценарий.** Playbook заточен под одну связку: Hermes — координатор, с которым вы говорите
(десктоп, CLI или Telegram), а он запускает воркеров Claude Code и Codex в Orca, каждого в своём
терминале и git worktree. Hermes планирует, распределяет, принимает и коммитит; тяжёлые правки
параллельно делают воркеры Orca. Правила и навыки работают и в чистом Claude Code или Codex, но части
про делегирование, жизненный цикл воркеров и приёмку рассчитаны на Hermes + Orca.

### Как это работает

![Как задача проходит через агентов](docs/how-it-works.png)

Владелец ставит задачу. Координатор (Hermes, Claude Opus 5.5) раскладывает её и выбирает исполнителя
по таблице §9 `global/GLOBAL_RULES.md`: механику (поиск, подсчёт, git, проверки) координатор делает сам
без модели; всё, что требует модели, — отдельный Orca-воркер на задачу: разведку, сводку и правки по
готовой спеке — Claude Opus 5.5 medium (low для простой разведки), тяжёлую разработку, архитектуру,
сложные правки и приёмку — Opus 5.5 high, роли — с моделью из профиля, разовые запросы, поиск в сети
и картинки — Codex `gpt-6-luna` xhigh. `delegate_task` и субагенты внутри сессии маршрутом не считаются;
Sonnet не используется (решение владельца 2026-09-28).

Самоотчёт исполнителя не считается фактом: координатор сверяет diff и прогоняет проверки проекта,
затем коммитит и отдаёт отчёт со ссылками `файл:строка`. Всё, что владелец должен посмотреть, выходит
веб-страницей: монитор прогонов симуляции, аналитический отчёт с графиками и развилками карточками,
прототип экрана. Страница публикуется внутри закрытой сети (Tailscale tailnet); перед выдачей ссылки
проверяются код 200 и скриншот headless-браузером. Если проблема не решается за 2–3 итерации, её
откладывают или несут владельцу (§12).

Интерактивная схема (поиск, фокус, трассировка связей, экспорт) — скачайте `docs/how-it-works.html`
и откройте в браузере. Исходник — `docs/how-it-works.workflow.json`, собран
[Archify](https://github.com/tt-a1i/archify):
`node bin/archify.mjs deliver workflow docs/how-it-works.workflow.json docs/how-it-works.html --quality showcase`.

### Состав

| Путь | Что | Куда ставится |
|---|---|---|
| `global/GLOBAL_RULES.md` | глобальные правила: принципы, язык и тон, маршрутизация моделей (§9), раскладка проекта (§10), навыки по умолчанию (§11), лимит итераций (§12), CPU (§13), результаты веб-страницами (§14), экономия контекста воркеров (§15) | `~/.agents/GLOBAL_RULES.md` + симлинки `%LOCALAPPDATA%\hermes\SOUL.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md` |
| `skills/<категория>/<имя>` | глобальные навыки Hermes (см. ниже) | `%LOCALAPPDATA%\hermes\skills\` |
| `project-template/` | каркас нового проекта: `CLAUDE.md`, процесс студии, роли, очередь задач | корень нового репозитория |
| `docs/startup-settings.md` | стартовые настройки машины для Hermes + Orca: каждый пункт с проверкой | выполняет агент после установки |

#### Навыки

| Навык | Когда |
|---|---|
| `agent-delegation-and-verification` | спека воркеру, проверка самоотчёта, приёмка, интеграция волны |
| `orca-worker-routing` | запуск Codex/Claude-воркеров через Orca, их цикл и ловушки |
| `agent-cost-monitoring` | цена блока в токенах, факт против оценки |
| `agent-project-setup` | новый проект: CLAUDE.md, `.claude/skills`, симлинки, доверие харнессов |
| `agent-harness-config` | единые правила и навыки в Hermes, Claude Code, Codex |
| `agent-settings-migration` | перенос настроек Hermes на другую машину |
| `hermes-gateway-ops`, `hermes-tool-backend-setup` | Telegram-шлюз, веб-бэкенды Hermes |
| `browser-page-preview` | дашборды, отчёты, прототипы и мониторы прогонов веб-страницами |
| `git-branch-integration` | сведение веток воркеров в master |
| `design-decision-interview` | закрытие развилок владельца по одной через `clarify` |
| `deck-from-sources` | короткая презентация из документов: порядок работы воркеров, ловушки рендера |
| `codex-web-search`, `video-transcript-research` | исследования |
| `game-*`, `3d-asset-generation` | игровые проекты: препродакшн, баланс-симуляции, прототипы UI, 3D |

Сторонние пакеты (`caveman`, `ponytail`, `archify`, Orca `orchestration`) не вендорятся — ставятся
из источников по `skills/autonomous-ai-agents/agent-project-setup/references/third-party-skill-packs.md`.

### Установка через агента (проще всего)

Вставьте это в Hermes, Claude Code или Codex на нужной машине:

```text
Установи agent playbook из https://github.com/wCELENw/agent-playbook на эту машину.
Действуй по разделу README «Установка вручную» и skills/autonomous-ai-agents/agent-project-setup/SKILL.md.
Перед копированием покажи, какие мои правила и навыки будут перезаписаны, и дождись моего OK.
Спроси у меня значения плейсхолдеров (<OWNER_CHAT_ID>, <tailnet>, имена машин, пути, лимиты CPU)
и впиши их только в установленные копии, не в клон.
Запиши установленный коммит в ~/.agents/agent-playbook.version.
В конце проверь, что каждый харнесс реально подгружает правила и навыки.
Затем прочитай docs/startup-settings.md и выполни каждый пункт, отчитавшись по его проверке.
```

Агент сам прочитает репозиторий, подгонит его под машину и спросит перед перезаписью.

### Установка вручную (Windows, git-bash)

```bash
git clone https://github.com/wCELENw/agent-playbook ~/agent-playbook
mkdir -p ~/.agents && cp ~/agent-playbook/global/GLOBAL_RULES.md ~/.agents/GLOBAL_RULES.md
# симлинки (Developer Mode): SOUL.md, ~/.claude/CLAUDE.md, ~/.codex/AGENTS.md -> ~/.agents/GLOBAL_RULES.md
cp -r ~/agent-playbook/skills/* "$LOCALAPPDATA/hermes/skills/"
git -C ~/agent-playbook rev-parse HEAD > ~/.agents/agent-playbook.version
# ранняя автосводка Claude Code (правило 15): env в ~/.claude/settings.json
python -c "import json,pathlib;p=pathlib.Path.home()/'.claude/settings.json';d=json.loads(p.read_text('utf-8')) if p.exists() else {};d.setdefault('env',{})['CLAUDE_CODE_AUTO_COMPACT_WINDOW']='300000';p.write_text(json.dumps(d,indent=2,ensure_ascii=False),'utf-8')"
```

Подробно, с проверкой загрузки в каждом харнессе, — `skills/autonomous-ai-agents/agent-project-setup/SKILL.md`.
Машинно-специфичные строки (хосты, chat_id, пути, модели) правятся под машину после копирования.

**Последний шаг, обязательный:** попросите агента «Прочитай docs/startup-settings.md в ~/agent-playbook
и выполни каждый пункт с проверкой». Он настроит на машине всё, на что опирается связка Hermes + Orca:
модели, доверие папок, звук, отключение claude-mem у воркеров, окружение Orca. Без этого воркеры
могут зависать или жечь токены.

### Новый проект

1. Скопировать `project-template/` в корень репозитория, заполнить `CLAUDE.md`.
2. Роли проекта — `.claude/agents/<роль>.md` по образцу `architect`/`doc-keeper`/`qa-tester`
   (модель и effort во frontmatter), зоны — в таблицу `docs/studio/STUDIO.md` §2.
3. `MSYS=winsymlinks:nativestrict ln -s ../.claude/skills .agents/skills`, `hermes skills trust .`.

### Регулярное обновление

Установленные копии подогнаны под вашу машину, поэтому обновление — это слияние, а не слепое
копирование. Скажите агенту:

```text
Обнови agent playbook: git pull в ~/agent-playbook, затем кратко перескажи, что изменилось с коммита
из ~/.agents/agent-playbook.version. Влей изменения в мои установленные правила и навыки, сохранив
мои значения и локальные правки; где конфликт — спроси. Обнови файл версии и повтори проверку загрузки.
```

Вручную:

```bash
cd ~/agent-playbook && git pull
git log --oneline "$(cat ~/.agents/agent-playbook.version)..HEAD"      # что нового
git diff "$(cat ~/.agents/agent-playbook.version)..HEAD" -- global skills  # влить руками
git rev-parse HEAD > ~/.agents/agent-playbook.version
```

Чтобы не забывать проверять: нажмите **Watch** на GitHub или поручите это Hermes по расписанию, например
`/cron add "0 10 * * 1" "Проверь github.com/wCELENw/agent-playbook на коммиты новее
~/.agents/agent-playbook.version и пришли короткую сводку; ничего не устанавливай."`

### Публикация своих изменений (для мейнтейнера)

Канон — рабочие файлы на машине (`~/.agents`, `%LOCALAPPDATA%\hermes\skills`). После правки навыка
или правил — скопировать в клон, заменить личные данные плейсхолдерами, прогнать
`bash scripts/check-public.sh` (он же стоит хуком `pre-push`) и закоммитить.

### Перед использованием

Это личная рабочая конфигурация, выложенная как пример. Плейсхолдеры `<OWNER_CHAT_ID>`, `<tailnet>`,
имена машин (`minipc`, `powerpc-1`), пути `C:\Users\user\…` и лимиты CPU замените на свои.
Секретов в репозитории нет: токены ботов и ключи API хранятся в `.env` проектов и сюда не попадают.

### Лицензия

[MIT](LICENSE) — используйте, меняйте и распространяйте свободно, сохраняя уведомление об авторстве.
Сторонние пакеты навыков (`caveman`, `ponytail`, `archify`, Orca `orchestration`) сюда не входят и
распространяются по своим лицензиям из своих репозиториев.
