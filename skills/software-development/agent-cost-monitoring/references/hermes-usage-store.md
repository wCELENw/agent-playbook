# Счётчики расхода Hermes (`state.db`)

Путь: `~/AppData/Local/hermes/state.db` (SQLite; на Windows — `C:\Users\<user>\AppData\Local\hermes\state.db`).
Обновляется на ходу; при чтении во время работы агента числа ещё растут.

## Таблицы

`session_model_usage` — накопленный расход по (сессия, модель, задача):

- `session_id`, `model`, `billing_provider`, `billing_base_url`, `task`;
- `api_call_count`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`,
  `reasoning_tokens`;
- `estimated_cost_usd`, `actual_cost_usd`, `cost_status`, `cost_source`, `first_seen`, `last_seen`.

`task = ''` — основной цикл; прочие значения (`title_generation`, `approval`) — служебные вызовы,
их тоже надо считать, они малы.

`sessions` — то же самое по сессии целиком, плюс `message_count`, `tool_call_count`, `model`,
`cwd`, `parent_session_id`, `started_at`, `last_activity_at`, `estimated_cost_usd`.

`messages` — `token_count` на сообщение (для разрезов по времени/темам, если нужны).

## Запросы

Точка отсчёта по текущей сессии (baseline перед этапом):

```
py -c "import sqlite3;c=sqlite3.connect(r'C:\Users\user\AppData\Local\hermes\state.db');\
print(list(c.execute(\"select api_call_count,input_tokens,output_tokens,cache_read_tokens \
from session_model_usage where session_id='<id>' and task=''\")))"
```

Рабочий вариант — считать в execute_code: точки до и после этапа, дельта и рубли одной функцией,
чтобы не переписывать формулу ставок на каждом шаге:

```python
IN, OUT, CACHE = 30.0, 120.0, 0.6   # ₽/1M: вход, выход, кэш — ставки провайдера этой модели
def rub(i, o, ca): return i/1e6*IN + o/1e6*OUT + ca/1e6*CACHE
def point(sid):
    row = list(c.execute("select sum(api_call_count),sum(input_tokens),sum(output_tokens),\
sum(cache_read_tokens) from session_model_usage where session_id=?", (sid,)))[0]
    return tuple(x or 0 for x in row)
# этап: before = point(SID) … этап … after = point(SID)
# факт этапа = rub(*after[1:]) - rub(*before[1:])
```

Точка отсчёта должна совпадать с той, от которой считался прошлый отчёт — иначе итог по фиче не сойдётся.

## Дети-субагенты

Расход дочерних сессий в `session_model_usage` координатора НЕ виден. Дети — отдельные сессии со
ссылкой на родителя:

```
py -c "import sqlite3;c=sqlite3.connect(r'C:\Users\user\AppData\Local\hermes\state.db');\
q='select id,api_call_count,input_tokens,output_tokens,cache_read_tokens from sessions \
where parent_session_id=? order by id';print(*c.execute(q,('<id родителя>',)),sep=chr(10))"
```

Полный расход этапа = дельта координатора + суммарный расход его детей, запущенных в этом этапе
(фильтровать по id/времени этапа — у координатора могут быть дети от прошлых этапов).

Полезное в выводе: `api_call_count` ребёнка — прямой ответ на «сколько уложился агент», а разница
`in`/`cache` показывает, перечитывал он проект или работал по указателям, переданным в задании.

## Что важно знать

- `input_tokens` — только НЕкэшированный вход; кэш считается отдельным полем (в Hermes
  `total = input + cache_read + cache_write`).
- `estimated_cost_usd` остаётся `0`, если в конфиге нет прайса модели — считать вручную по ставкам
  провайдера. `billing_base_url` — настоящий адрес, через который идёт счёт (проверять, что это
  тот же провайдер, чьи тарифы вы взяли).
- Таблицы `sessions` и `session_model_usage` дают разные цифры по одному и тому же интервалу
  (по-разному разносят кэш): для отчётов держаться одной таблицы от baseline до финала.
- Сессия ребёнка (субагента) может быть отдельной записью с `parent_session_id` — см. раздел выше.
- Контекстное окно и лимиты вывода — в `context_length_cache.yaml` рядом; полезно, чтобы понять,
  сколько вызовов уйдёт на один прогон харнесса или длинный файл.
