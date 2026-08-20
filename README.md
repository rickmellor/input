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
