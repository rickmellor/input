# qchat

Zero-overhead chat REPL + shell-command generator for local OpenAI-compatible seats
(johnny fleet). Stdlib-only Python, single file.

- `qchat` — chat REPL on the gemma seat; thinking models stream reasoning dimmed
- `qchat coder` / `qchat gemma` / `qchat qwen38` — seat shortcuts (or `qchat <model> <base_url>`)
- `/models` — toggle seats mid-conversation (live up/down status, history carries)
- `qchat -e <task>` — NL → shell command via the coder seat (thinking off), then
  `execute | revise | describe | copy | quit`
- `qchat -x <task>` — same, but executes immediately
- bare `qchat -e` / `-x` — prompts for the task (no shell quoting hazards)

Install: symlink `qchat` onto your PATH (`ln -s ~/repos/qchat/qchat ~/.local/bin/qchat`).

Planned: butterfish-style `!` / `!!` goal mode via bash `command_not_found_handle`.

## Shell integration (v2)

Source once from `~/.bashrc`:

    source ~/repos/qchat/qchat-shell.bash

- `!<task>`  — goal agent: proposes each step, you confirm, it runs and observes output
- `!!<task>` — autonomous agent: hardcoded catastrophic-command denylist (always blocks)
  + gemma risk review; auto-runs only none/low risk, drops to manual confirm on medium+
- `Ctrl-G`   — turn the current line's natural language into a command, editable in the
  buffer (runs in your real shell on Enter, so cd/exports/history behave normally)

Needs history expansion off (`set +H`, which the integration sets) so `!` is literal.
Recent shell history is passed as context, so "!why did that fail" works.
