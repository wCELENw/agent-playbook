"""Coordinator inbox watcher for Orca workers when the coordinator is Hermes in the gateway
(Telegram): it gets no worker messages unless it checks the inbox itself.
Blocks on `orca orchestration check --wait`, prints worker_done/question/escalation, acks the
delivery, exits. Run as terminal(background=true, notify=true); the exit wakes the coordinator.
Re-arm after every wake. Heartbeat-only deliveries are acked silently.
Usage: python watch_orca_inbox.py <coordinator_terminal_handle> [max_seconds]"""
import json, subprocess, sys, time

T = sys.argv[1]
deadline = time.time() + float(sys.argv[2] if len(sys.argv) > 2 else 14400)


def orca(*a):
    s = subprocess.run(["orca", "orchestration", *a, "--json"], capture_output=True, text=True,
                       encoding="utf-8", shell=True).stdout
    return json.JSONDecoder().raw_decode(s[s.find("{"):])[0].get("result", {})


while time.time() < deadline:
    left = int((deadline - time.time()) * 1000)
    r = orca("check", "--terminal", T, "--wait", "--types", "worker_done,escalation,question",
             "--timeout-ms", str(min(max(left, 1000), 600000)))
    real = [m for m in r.get("messages", []) if m["type"] != "heartbeat"]
    for m in real:
        print(m["type"], m["from_handle"], m["id"], "\n", m["body"][:1500], "\n====")
    if r.get("deliveryId"):
        orca("check", "--terminal", T, "--ack", r["deliveryId"])
    if real:
        break
else:
    print("timeout")
