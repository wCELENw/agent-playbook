"""Pull agent-playbook and update local copies of global rules and Hermes skills.

Only copies untouched since the last sync are updated; local edits are reported
(LOCAL / CONFLICT) and left alone. See GLOBAL_RULES.md section 16.

Usage: py scripts/sync_playbook.py [--dry-run] [--no-pull] [--adopt]
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r", b"")).hexdigest()


def pairs(hermes, agents):
    for src in sorted((REPO / "skills").rglob("*")):
        if src.is_file() and "__pycache__" not in src.parts:
            rel = src.relative_to(REPO)
            yield rel.as_posix(), src, hermes / rel
    yield "global/GLOBAL_RULES.md", REPO / "global/GLOBAL_RULES.md", agents / "GLOBAL_RULES.md"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-pull", action="store_true")
    ap.add_argument("--adopt", action="store_true")
    args = ap.parse_args(argv)

    hermes = Path(os.environ.get("HERMES_HOME") or Path(os.environ["LOCALAPPDATA"]) / "hermes")
    agents = Path(os.environ.get("AGENTS_HOME") or Path.home() / ".agents")
    state_file = agents / "agent-playbook.sync.json"
    log_file = agents / "agent-playbook.sync.log"
    stamp = datetime.now()
    lines = []

    def finish(code):
        for line in lines:
            print(line)
        if not args.dry_run:
            agents.mkdir(parents=True, exist_ok=True)
            with log_file.open("a", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in lines)
        return code

    if not args.no_pull:
        r = subprocess.run(["git", "-C", str(REPO), "pull", "--ff-only"], capture_output=True, text=True)
        if r.returncode:
            lines.append(f"{stamp:%Y-%m-%d %H:%M:%S} ERROR git pull: {(r.stderr or r.stdout).strip()}")
            return finish(1)

    state = json.loads(state_file.read_text("utf-8")) if state_file.exists() else {}
    new_state = dict(state)
    backup = agents / f"playbook-backup-{stamp:%Y%m%d-%H%M%S}"
    counts = {}
    details = []

    for rel, src, dst in pairs(hermes, agents):
        repo_hash = digest(src)
        if not dst.exists():
            action = "INSTALL"
        else:
            local = digest(dst)
            if local == repo_hash:
                action = "OK"
            elif local == state.get(rel):
                action = "UPDATE"
            elif args.adopt:
                action = "ADOPT"
            elif rel not in state or state[rel] != repo_hash:
                action = "CONFLICT"
            else:
                action = "LOCAL"
        counts[action] = counts.get(action, 0) + 1
        if action in ("CONFLICT", "LOCAL"):
            details.append(f"  {action} {rel} -> {dst}")
            continue
        new_state[rel] = repo_hash
        if action == "OK":
            continue
        details.append(f"  {action} {rel} -> {dst}")
        if args.dry_run:
            continue
        if action == "ADOPT":
            (backup / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dst, backup / rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    r = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True)
    head = r.stdout.strip() if r.returncode == 0 else "no-git"
    summary = " ".join(f"{k}={counts.get(k, 0)}" for k in ("OK", "INSTALL", "UPDATE", "ADOPT", "LOCAL", "CONFLICT"))
    lines.append(f"{stamp:%Y-%m-%d %H:%M:%S} HEAD={head[:12]} {summary}{' (dry-run)' if args.dry_run else ''}")
    lines.extend(details)

    if not args.dry_run:
        agents.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(new_state, indent=1, sort_keys=True), "utf-8")
        if r.returncode == 0:
            (agents / "agent-playbook.version").write_text(head + "\n", "utf-8")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
