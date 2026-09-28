# Сторонние пакеты навыков/плагинов (caveman, ponytail и т.п.) в Hermes, Codex, Claude Code

## Оценка до установки («насколько применим к нашему процессу»)

Когда владелец спрашивает о пользе, а не просит поставить, сначала оценка, установка — только по решению.

1. Клон в scratch (`git clone --depth 1`), `git log -1` (свежесть), состав: `skills/`, `hooks/`,
   `.hermes-plugin`/`.claude-plugin`/`.codex-plugin`, `wc -w skills/*/SKILL.md` (цена в токенах).
2. **Хук старта сессии читать первым** (`hooks/session-start`, `__init__.py` плагина): что он
   инжектит в КАЖДУЮ сессию и после compact. Блоки вида «вызывай навык при 1 % шансе», обязательные
   объявления «Using X» — прямой конфликт с caveman/кратким форматом и ролью координатора.
3. Уже установленное пересечение: `grep -l -i '<owner>/<repo>\|adapted from' $HERMES_HOME/skills/*/*/SKILL.md`
   — часть навыков пакета часто уже стоит адаптацией (напр. `systematic-debugging`, `test-driven-development`,
   `requesting-code-review` — из obra/superpowers).
4. **Мерка — универсальный процесс владельца, а не один проект.** «Наш воркфлоу» = `~/.agents/GLOBAL_RULES.md`
   (§9 маршрутизация через Orca, §10 раскладка) + глобальные навыки (`agent-delegation-and-verification`,
   `orca-worker-routing`) + шаблон проекта из playbook владельца (github.com/wCELENw/agent-playbook:
   `project-template/docs/studio/{STUDIO,common,ORCA}.md`, роли `.claude/agents/`). Проектный
   `CLAUDE.md` (напр. мода) — только если владелец назвал проект: иначе выводы оказываются узкими и
   владелец их отвергает. Сверять жёсткие гейты пакета (brainstorming перед любой работой, TDD,
   worktrees, дешёвые модели, subagents внутри сессии вместо Orca-воркеров) с этими правилами.
4a. **Сначала искать ту же идею у себя** (`grep -rn -i '<ключевое слово>'` по playbook и
   `$HERMES_HOME/skills`): часто она уже есть, и реальная находка — противоречие между своими
   документами (напр. правило «на каждый блок» против «проверки по риску»), а не заимствование.
   Опубликованный playbook может отставать от локальных `GLOBAL_RULES`/навыков — `diff` их и
   сказать владельцу.
4b. **Заимствуемую дорогую практику (состязательная приёмка, мутационные пробы, доп. проход)
   предлагать с триггером по риску и бюджетом**, а не «всегда»: по каждому классу задач — окупается
   ли, чем уже покрыто механическими проверками, лимит попыток, какие находки блокируют. Дешёвое
   правило (PASS только с командой и выводом) — можно везде.
5. Телеметрия/сеть: `grep -n -i telemetry README.md` и env отключения.
6. Вывод: «ставить целиком / точечно / нет» + список конкретных идей для переноса в глобальные
   правила/навыки или шаблон проекта (со строками-источниками `файл:N`) + конфликты. Глобальная установка
   затрагивает все проекты — сказать явно; альтернатива — project-scope без хука старта.
   Сказать, какие навыки прочитаны целиком, а какие оценены по структуре разделов.

## Установка в Hermes

1. **Склонировать репо в scratch** (`git clone --depth 1 -q <url>`), а не читать README через
   web_extract: нужен весь каталог — `plugin.yaml`/`plugin.json`, `__init__.py`, инсталлятор.
   Сразу найти путь автора для каждого харнесса: `grep -n -i -A8 'hermes\|codex' README.md INSTALL.md bin/*.js`.
   Авторы часто поставляют отдельный маршрут для Hermes — он точнее общего `npx skills add`.
2. **Определить тип пакета**:
   - только SKILL.md → инсталлятор автора (напр. `node bin/install.js --only hermes`), сначала
     `--dry-run`, чтобы увидеть целевой каталог (`$HERMES_HOME/skills/<category>/`);
   - `plugin.yaml` + `__init__.py` (хуки `pre_llm_call`, слэш-команды) → `hermes plugins install
     owner/repo --enable`.
3. **Сканер плагинов** на community-источнике даёт CAUTION/BLOCKED из-за шума в benchmarks/,
   examples/, CI. Смотреть только серьёзные находки:
   `... 2>&1 | grep -v -E '^\s*LOW' | grep -E -A1 'CRITICAL|HIGH|MEDIUM|Verdict'` и отдельно
   проверить сам загружаемый код: `grep -n -E 'import|subprocess|urllib|socket|exec\(|eval\(' __init__.py`.
   Только после этого `--force`.
4. **Если установщик отвергает `plugin.json`** («unsupported or missing Agent Plugins schema») при
   наличии рабочего `plugin.yaml` — это заглушка для других харнессов; ставить вручную:
   `git clone --depth 1 <url> "$HERMES_HOME/plugins/<name>" && hermes plugins enable <name>`.
   Такой плагин не обновляется через `hermes plugins update` — обновление `git pull` в его каталоге;
   сказать об этом владельцу.
5. **Проверить загрузку движком**, а не строкой в `hermes plugins list`:
   ```
   cd "$HERMES_HOME/hermes-agent" && ./venv/Scripts/python.exe -c "
   from hermes_cli.plugins import PluginManager
   m=PluginManager(); m.discover_and_load(); p=m._plugins['<name>']
   print(p.enabled, p.error, p.hooks_registered, p.commands_registered)"
   ```
   Навыки — `hermes skills list | grep <name>`. Всё вступает в силу со следующей сессии.
6. Удалить клоны из scratch.

## Режим «включён по умолчанию» во всех харнессах

Сначала инвентаризация: что уже стоит и где. Режим по умолчанию у таких пакетов обычно
читается из `%APPDATA%\<pack>\config.json` (`{"defaultMode": "full"}`) или env
`<PACK>_DEFAULT_MODE` — его разделяют хуки Claude Code и плагин Hermes.

| Харнесс | Пакет с хуком/плагином | Пакет из одних навыков |
|---|---|---|
| Hermes | плагин с `pre_llm_call` сам инжектит режим; проверка — импорт `__init__.py` и `build_injected_context()` / `_default_mode()` | `hermes config set skills.auto_load '["<skill>"]'`; проверка `from agent.skill_commands import resolve_auto_load_skills` |
| Claude Code | `enabledPlugins` в `~/.claude/settings.json` + SessionStart-хук плагина | то же через плагин автора |
| Codex | хуки плагинов не исполняются (`codex features list` → `plugin_hooks removed`); плагин даёт только навыки | навык в `~/.agents/skills` (`npx -y skills add <owner/repo> --skill <name> -a codex -g -y`) |

Codex always-on — строка `developer_instructions = "..."` верхнего уровня в `config.toml`
(после `project_doc_fallback_filenames`), называющая навыки и уровень: «follow skill `X` (level
full) from the first reply…». Перед правкой — `cp config.toml config.toml.pre-<topic>.bak`.

Ловушки:
- **Под Orca у Codex два дома** (`~/.codex` и `%APPDATA%\orca\codex-runtime-home\home`);
  `plugins/` и `skills/` Orca-дома — симлинки на `~/.codex`, а `config.toml` у каждого свой.
  Плагин ставить с `CODEX_HOME='C:\Users\user\.codex'` и без него (секции `[plugins."x@y"]` и
  `[marketplaces.*]` пишутся в конфиг текущего дома), `developer_instructions` — в оба config.toml.
- **Маркетплейс автора может не подходить Codex**: если в корне репо есть только
  `.claude-plugin/marketplace.json`, `codex plugin add` ставит пакет без `.codex-plugin` → навыки
  не попадают в промпт. Одноимённый плагин в `openai-curated-remote` бывает от другого автора и
  с другим содержимым — сверять `author` в его `.codex-plugin/plugin.json`. В таком случае
  удалить плагин и маркетплейс и ставить навык через `npx skills add`.
- **Проверка Codex — только по реальному промпту**: `codex debug prompt-input hi > file` и grep
  по тексту `developer_instructions` и `- <skill>:` — для каждого дома отдельно.
- **Ручной прогон хуков Claude Code**: `CLAUDE_PLUGIN_ROOT` и путь скрипта передавать как
  `C:/Users/...` — в формате `/c/Users/...` node на Windows ищет `C:\c\Users\...` и падает с
  MODULE_NOT_FOUND. Ожидаемый вывод: `<PACK> MODE ACTIVE — level: full`.
- Всё действует только с новой сессии — сказать владельцу.

## Отчёт владельцу

- Как включать/выключать (always-on или по команде, фраза отключения, env/config режима).
- Какие харнессы получили режим каким механизмом (хук / auto_load / developer_instructions) и чем
  проверено; где лежат `.bak` конфигов.
- **Конфликты с `~/.agents/GLOBAL_RULES.md`** назвать явно (напр. «пещерный» стиль caveman full
  против тона Альфреда) и предложить развилку (смягчить правило или понизить уровень) — решение
  за владельцем.
- Если Orca может пересобрать свой config.toml — предупредить, что ручную строку придётся вернуть.
