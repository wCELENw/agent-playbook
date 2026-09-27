"""Show or set Orca per-agent env (settings.agentDefaultEnv).

Where Orca keeps settings depends on its version:
- newer (seen in 1.4.215): SQLite <profile>/profile-state.db, table profile_state_documents,
  row domain='settings', JSON in payload, content_hash = sha256(payload) hex;
  orca-data.json is then only an export;
- older (seen in 1.4.210): no usable profile-state.db, settings live in
  <profile>/orca-data.json under "settings".
<profile> = %APPDATA%/orca/profiles/local-default (override: ORCA_PROFILE_DIR).

  python orca_agent_env.py                               # show the store and agentDefaultEnv
  python orca_agent_env.py --set claude CLAUDE_MEM_INTERNAL 1

--set only with Orca fully closed (every Orca.exe except daemon-host): Orca holds
settings in memory and overwrites the edit. The store is backed up first.
"""
import hashlib, json, os, shutil, sqlite3, sys, time

PROFILE = os.environ.get('ORCA_PROFILE_DIR') or os.path.join(
    os.environ['APPDATA'], 'orca', 'profiles', 'local-default')
DB = os.path.join(PROFILE, 'profile-state.db')
JSON = os.path.join(PROFILE, 'orca-data.json')


def sqlite_settings():
    # mode=rw: never create an empty DB where Orca does not use one
    if not os.path.isfile(DB) or os.path.getsize(DB) == 0:
        return None
    con = sqlite3.connect(f'file:{DB}?mode=rw', uri=True)
    try:
        return con.execute("select payload, revision from profile_state_documents "
                           "where domain='settings'").fetchone()
    except sqlite3.OperationalError:
        return None
    finally:
        con.close()


def backup(paths):
    stamp = time.strftime('%Y%m%d-%H%M%S')
    for p in paths:
        if os.path.exists(p):
            shutil.copy2(p, f'{p}.bak-{stamp}')
    return stamp


row = sqlite_settings()
if row:
    payload, rev = row
    settings, where = json.loads(payload), DB
else:
    data = json.load(open(JSON, encoding='utf-8'))
    settings, where = data.setdefault('settings', {}), JSON

if len(sys.argv) == 1:
    print(where)
    print(json.dumps(settings.get('agentDefaultEnv', {}), indent=2))
    sys.exit(0)
if len(sys.argv) != 5 or sys.argv[1] != '--set':
    sys.exit(__doc__)
agent, key, value = sys.argv[2:]
settings.setdefault('agentDefaultEnv', {}).setdefault(agent, {})[key] = value

if row:
    stamp = backup([DB, DB + '-wal', DB + '-shm'])
    new = json.dumps(settings, ensure_ascii=False, separators=(',', ':'))
    con = sqlite3.connect(f'file:{DB}?mode=rw', uri=True)
    con.execute(
        "update profile_state_documents set payload=?, content_hash=?, revision=?, updated_at=? "
        "where domain='settings'",
        (new, hashlib.sha256(new.encode('utf-8')).hexdigest(), rev + 1, int(time.time() * 1000)))
    con.commit()
    con.close()
else:
    stamp = backup([JSON])
    with open(JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
print(f'{where}: agentDefaultEnv.{agent}.{key}={value}, backup *.bak-{stamp}')
