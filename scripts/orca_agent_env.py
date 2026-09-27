"""Show or set Orca per-agent env (settings.agentDefaultEnv).

Orca keeps settings in SQLite, not in orca-data.json (that file is an export):
%APPDATA%/orca/profiles/local-default/profile-state.db, table profile_state_documents,
row domain='settings', JSON in payload, content_hash = sha256(payload) hex.

  python orca_agent_env.py                               # show agentDefaultEnv
  python orca_agent_env.py --set claude CLAUDE_MEM_INTERNAL 1

--set only with Orca fully closed (every Orca.exe except daemon-host): Orca holds
settings in memory and overwrites the edit. A backup of profile-state.db* is made first.
"""
import hashlib, json, os, shutil, sqlite3, sys, time

DB = os.environ.get('ORCA_PROFILE_DB') or os.path.join(
    os.environ['APPDATA'], 'orca', 'profiles', 'local-default', 'profile-state.db')

con = sqlite3.connect(DB)
payload, rev = con.execute(
    "select payload, revision from profile_state_documents where domain='settings'").fetchone()
settings = json.loads(payload)

if len(sys.argv) == 1:
    print(json.dumps(settings.get('agentDefaultEnv', {}), indent=2))
    sys.exit(0)

if len(sys.argv) != 5 or sys.argv[1] != '--set':
    sys.exit(__doc__)
agent, key, value = sys.argv[2:]
con.close()
stamp = time.strftime('%Y%m%d-%H%M%S')
for suffix in ('', '-wal', '-shm'):
    if os.path.exists(DB + suffix):
        shutil.copy2(DB + suffix, f'{DB}{suffix}.bak-{stamp}')
con = sqlite3.connect(DB)
settings.setdefault('agentDefaultEnv', {}).setdefault(agent, {})[key] = value
new = json.dumps(settings, ensure_ascii=False, separators=(',', ':'))
con.execute(
    "update profile_state_documents set payload=?, content_hash=?, revision=?, updated_at=? "
    "where domain='settings'",
    (new, hashlib.sha256(new.encode('utf-8')).hexdigest(), rev + 1, int(time.time() * 1000)))
con.commit()
print(f'set agentDefaultEnv.{agent}.{key}={value}, revision {rev + 1}, backup *.bak-{stamp}')
