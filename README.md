# input

> Formerly **qchat**. The command, config dir (`~/.config/input`), and repo were renamed to `input`; a `qchat` symlink is kept as a back-compat alias.

Zero-overhead chat REPL + shell-command generator for local OpenAI-compatible seats
(johnny fleet). Stdlib-only Python, single file.

- `input` — chat REPL on the gemma seat; thinking models stream reasoning dimmed
- `input coder` / `input gemma` / `input qwen38` — seat shortcuts (or `input <model> <base_url>`)
- `/models` — toggle seats mid-conversation (live up/down status, history carries)
- `input -e <task>` — NL → shell command via the coder seat (thinking off), then
  `execute | revise | describe | copy | quit`
- `input -x <task>` — same, but executes immediately
- bare `input -e` / `-x` — prompts for the task (no shell quoting hazards)

Install: symlink `input` onto your PATH (`ln -s ~/repos/input/input ~/.local/bin/input`).

Planned: butterfish-style `!` / `!!` goal mode via bash `command_not_found_handle`.

## Sub-agents and seat guidance

`spawn_agent` hands a self-contained unit of work to a sub-agent on a chosen seat, so an
orchestrating model can decompose a task and delegate the execution. Pin the seat with
`model` (`coder`, `cloud-large`, …); omit it and the brief is classified and routed.

Pins are passed through to the router as-is, and SAINT honours a pin only when it is written
as a full `saint-<backend>` id — a short form falls through to the classifier. So callers
generally pass `saint-local-coder`, not `coder`.

### Guidance: an ordered brief for a weak-planning seat

Some models execute delegated work well but plan it poorly — they converge badly on long
tool loops while handling a single well-scoped task fine. For those, a brief that spells out
the sequence beats an open-ended question.

That is a property of the *seat*, not of the task, so it is declared where seats are declared
— in the johnny profile — and read at spawn time:

```yaml
# ~/.config/johnny/profiles.yaml — seats is a list; the role is a field on each seat
seats:
  - model: <model-id>
    placement: <placement-id>
    role: chat
    guidance: roadmap      # this seat wants an explicit ordered brief
```

```
johnny resolve <role> --json   →   { "guidance": "roadmap", ... }
```

When `spawn_agent` sees `roadmap` for the seat it is about to use, it appends `_ROADMAP_BRIEF`
to that sub-agent's system prompt: work the brief in the order given, do not re-plan it, run
one step at a time and read each result before the next, and when a step is ambiguous pick one
option and say why rather than exploring. A seat that declares nothing gets a bare brief.

The lookup is best-effort and cached briefly — if `johnny` is unavailable the agent simply runs
without guidance. Seat names are normalised first (`seat_key`), so a full `saint-local-coder`
pin still finds the `coder` role that johnny knows.

To check what a sub-agent actually received, require it to open its answer with:

```
SEAT: <the seat and model you are running on>
GUIDANCE: <quote verbatim any instruction you were given about how to plan or
           sequence your work, or the word "none">
```

A guided seat quotes the brief; an unguided one says `none`. Running one of each in the same
task makes the difference visible.

### Sandbox

A sub-agent's `bash` is shell-less — one command per call, no pipes, redirects, globs, loops
or `&&`; only a `write=true` agent gets `bash -c '…'`. Write briefs as discrete steps, one
command each. The sandbox root is the `cwd` given to `spawn_agent`, and reads/writes outside
it are refused; a write-enabled agent gets that directory created if it is missing.

## Shell integration (v2)

Source once from `~/.bashrc`:

    source ~/repos/input/input-shell.bash

- `!<task>`  — goal agent: proposes each step, you confirm, it runs and observes output
- `!!<task>` — autonomous agent: hardcoded catastrophic-command denylist (always blocks)
  + gemma risk review; auto-runs only none/low risk, drops to manual confirm on medium+
- `Ctrl-G`   — turn the current line's natural language into a command, editable in the
  buffer (runs in your real shell on Enter, so cd/exports/history behave normally)

Needs history expansion off (`set +H`, which the integration sets) so `!` is literal.
Recent shell history is passed as context, so "!why did that fail" works.
