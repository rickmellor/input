# Example qchat user tool.
#
# Drop a copy in ~/.config/qchat/tools/ (any *.py there is loaded at REPL start) and the
# model can call it. A file defines either TOOL (one dict) or TOOLS (a list of dicts).
# Each dict needs:
#   name        unique tool name (snake_case)
#   description what it does + WHEN to call it — the model routes on this, so be specific
#   parameters  JSON Schema for the arguments (use {"type":"object","properties":{}} for none)
#   run         callable(args: dict) -> str   (the string is returned to the model as the result)
#
# NOTE: user tools run in-process with no sandbox and auto-execute when the model calls
# them — only add tools you'd be comfortable running unattended. Side-effecting tools
# (writes, network, shell) are your responsibility; keep them read-only unless you mean it.

import subprocess


def run(args):
    lines = int(args.get("lines", 10))
    out = subprocess.run(["journalctl", "--user", "-n", str(lines), "--no-pager"],
                         capture_output=True, text=True)
    return (out.stdout or out.stderr or "(no output)").strip()


TOOL = {
    "name": "recent_user_logs",
    "description": "Return the most recent systemd --user journal lines. Call when the "
                   "user asks what a service did recently, or to debug a local daemon.",
    "parameters": {
        "type": "object",
        "properties": {
            "lines": {"type": "integer", "description": "How many log lines (default 10)"},
        },
        "required": [],
    },
    "run": run,
}
