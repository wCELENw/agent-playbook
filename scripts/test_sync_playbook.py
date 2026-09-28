"""Self-check for sync_playbook.py: fake repo (no git) + temp HERMES_HOME/AGENTS_HOME.

Run: py scripts/test_sync_playbook.py  (exit 0 = pass)
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "sync_playbook.py"


def main():
    tmp = Path(tempfile.mkdtemp())
    try:
        repo, hermes, agents = tmp / "repo", tmp / "hermes", tmp / ".agents"
        (repo / "scripts").mkdir(parents=True)
        shutil.copy(SCRIPT, repo / "scripts")
        env = dict(os.environ, HERMES_HOME=str(hermes), AGENTS_HOME=str(agents))

        def put(path, data):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

        def run(*flags):
            r = subprocess.run([sys.executable, str(repo / "scripts/sync_playbook.py"), "--no-pull", *flags],
                               env=env, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr
            return r.stdout

        def local(rel):
            return (hermes / rel).read_bytes()

        a, b, c, d = "skills/x/a/SKILL.md", "skills/x/b/SKILL.md", "skills/x/c/SKILL.md", "skills/x/d/SKILL.md"
        for rel in (a, b, c, d):
            put(repo / rel, b"v1\n")
        put(repo / "skills/x/a/__pycache__/m.pyc", b"junk")
        put(repo / "global/GLOBAL_RULES.md", b"rules\r\n")
        put(hermes / "skills/x/own/SKILL.md", b"mine")  # local-only, must survive

        out = run()
        assert "INSTALL=5" in out, out
        assert local(a) == b"v1\n" and (agents / "GLOBAL_RULES.md").read_bytes() == b"rules\r\n"
        assert not (hermes / "skills/x/a/__pycache__").exists()

        # CRLF-insensitive: local CRLF vs repo LF counts as OK
        put(hermes / d, b"v1\r\n")
        assert "OK=5" in run(), "OK / CRLF"

        # b: repo changed, local untouched -> UPDATE
        put(repo / b, b"v2\n")
        # c: local edited, repo same -> LOCAL
        put(hermes / c, b"local edit\n")
        # a: local edited and repo changed -> CONFLICT
        put(repo / a, b"v2\n")
        put(hermes / a, b"local edit\n")
        out = run()
        assert "UPDATE=1" in out and "LOCAL=1" in out and "CONFLICT=1" in out, out
        assert local(b) == b"v2\n"
        assert local(c) == b"local edit\n" and local(a) == b"local edit\n"

        # dry-run writes nothing
        put(repo / b, b"v3\n")
        log_before = (agents / "agent-playbook.sync.log").read_text("utf-8")
        assert "UPDATE=1" in run("--dry-run")
        assert local(b) == b"v2\n"
        assert (agents / "agent-playbook.sync.log").read_text("utf-8") == log_before

        # --adopt: back up local edits, overwrite with repo
        out = run("--adopt")
        assert "ADOPT=2" in out and "UPDATE=1" in out, out
        assert local(a) == b"v2\n" and local(c) == b"v1\n" and local(b) == b"v3\n"
        backups = list(agents.glob("playbook-backup-*"))
        assert len(backups) == 1 and (backups[0] / a).read_bytes() == b"local edit\n"
        assert (hermes / "skills/x/own/SKILL.md").read_bytes() == b"mine"
        assert "OK=5" in run()
        print("ok")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
