# Example qchat user tool.
#
# Drop a copy in ~/.config/qchat/tools/ (any *.py there is loaded at REPL start) and the
# model can call it. A file defines either TOOL (one dict) or TOOLS (a list of dicts).
# Each dict needs:
#   name        unique tool name (snake_case)
#   description what it does + WHEN to call it — the model routes on this, so be specific
#   parameters  JSON Schema for the arguments (use {"type":"object","properties":{}} for none)
#   run         callable(args: dict) -> str   (the string is returned to the model as the result)
#   confirm     optional gate policy (default "never"):
#                 "never"   run automatically when the model calls it
#                 "always"  show the call and prompt y/N before running
#                 "review"  if the args have a "command" string, gemma rates its risk
#                           (none/low auto-run, medium+ prompt); the catastrophic denylist
#                           always prompts. This is what the built-in run_command uses.
#   display     optional result view (default "compact"):
#                 "compact" the result line is summarized to one line (large output stays
#                           readable); the model still receives the full text
#                 "full"    the whole result is printed under a gutter (use for output the
#                           user should see verbatim, e.g. a directory listing)
#
# NOTE: user tools run in-process with no sandbox. A "never" tool auto-executes when the
# model calls it — keep those read-only. For anything that writes, deletes, or reaches the
# network, set confirm="always" (or "review" if it takes a shell "command") so you get a
# prompt before it runs.

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
