# input

> Formerly **qchat**. The command, config dir (`~/.config/input`), and repo were renamed to
> `input`; a `qchat` symlink is kept as a back-compat alias.

A terminal agent client for local + cloud model fleets. Single-file, stdlib-only Python.
It started as a chat REPL and grew into the thing that actually does the work: it runs
tools, delegates to sub-agents, works autonomously toward a goal, executes stored plans,
and carries memory between sessions.

```
input                      # chat
input -e "<task>"          # natural language → shell command, then execute/revise/copy
input -x "<task>"          # same, run it immediately
input --goal "<criteria>"  # work autonomously until the criteria are met
input --resume [id|last]   # reopen a saved session   (--sessions lists them)
```

Install: symlink onto your PATH — `ln -s ~/repos/input/input ~/.local/bin/input`.

## Routing

input has **no static seat list**. It reads a [SAINT](https://github.com/rickmellor/saint-router)
router's `/status` on startup and reflects whatever is actually there — local seats managed by
[johnny](https://github.com/rickmellor/johnny), cloud tiers, and the classifier that picks
between them. Everything goes through the router; dormant seats simply don't appear.

- **Enter** sends to the active seat (`saint-auto` — the router classifies each message)
- **Ctrl+Enter** picks a seat for one message
- **F7–F12** one-shot to a specific seat, bound in ascending cost order
- **Ctrl+R** peeks the routing shortcuts, or per-flag help for a staged `/command`
- `/models`, `/seats` — switch the active seat, or show the discovered fleet

Seats are displayed in one unit — **$/Mtok of output** — so local (electricity) and cloud
(list price) are directly comparable.

## Agents and autonomy

- **`/goal <criteria>`** — the agent works toward an exit criterion across as many tool
  rounds as it takes. It stops when the goal is met, when it hits a hard block (a secret, a
  destructive step, a decision only you can make) and asks, or when it stalls.
- **`/jobs`** — detached background work with a status table: `run`, `build`, `review`,
  plus `log`, `stop`, and `answer` for a job that got blocked.
- **Sub-agents** — the agent delegates self-contained units of work to other seats. See
  below.
- **`/sidebar`** — fork an aside without polluting the main thread; `/merge` folds its
  conclusion back, `/return` parks it.

### Which one?

Three ways to hand off work, distinguished by what decides when they stop:

| | ends when | can ask you a question | use it for |
|---|---|---|---|
| `/goal` | the criteria are met | yes — parks as `BLOCKED:` | one outcome, worked in this session |
| `/jobs` | the goal is met, or it fails | yes — `/jobs answer <id>` resumes it | one outcome, worked in the background |
| `/loop` | you stop it (or it stops itself) | **no** — nobody is watching an iteration | a standing instruction, on a cadence |

Jobs and loops look alike — both are detached processes running the same engine, and a loop
iteration is literally a trimmed job runner — but the control model is opposite. **A job is
condition-driven: "am I done yet?"** It persists, retries, and parks to ask you when it hits an
ambiguity, because someone asked for that specific outcome. **A loop is time-driven: "is it time
yet?"** Completion is incidental; an iteration is a bounded errand that reports and exits.

That difference is why a loop iteration is told outright that nobody can answer it. A loop firing
at 6am has no one to ask, so blocking would be a silent hang rather than a useful pause.

## Loops — durable scheduled work

`/loop` runs a prompt repeatedly. Unlike an in-session timer, a loop **outlives the terminal**:
it lives in `~/.config/input/loops/<id>/` and is fired by a small scheduler daemon, so it keeps
running after you exit and comes back after a reboot.

```
/loop 10m check whether the bench finished      # fixed cadence
/loop every day at 6am summarise overnight CI   # calendar
/loop check CI and address review comments      # self-paced: the model picks 1min–1h each time
/loop                                           # list
/loop show|log|run|pause|resume|stop|rm <id>
/loop daemon                                    # install + start the scheduler
```

Iterations run on a **cheap local seat** by default — polling is mechanical, and a cloud seat on
a short cadence bills continuously. Each iteration reports only what changed; a quiet one is
suppressed rather than printed, so a loop that finds nothing stays silent.

A self-paced loop ends itself when its purpose is served. Any loop can be stopped with
`/loop stop <id>`.

### Durability

Loops are owned by a scheduler daemon (`input --loopd`, one systemd user unit). `/loop harden
<id>` promotes a single loop to **its own systemd timer**, so it fires even if the daemon is
down; `/loop unharden <id>` hands it back.

Missed fires — the machine was asleep, or off for a week — are guarded three ways, because a
scheduler that catches up naively floods you on the next boot:

- **coalesced** — a week of missed fires is one fire, not a week of them
- **skipped when stale** — a fire older than the loop's catch-up window is dropped and logged as
  `skipped_stale` rather than run days late
- **staggered** — survivors are spread out, with a cap on concurrent iterations

A loop that must run at an exact time needs a machine that is on at that time; catch-up makes it
fire *late*, not on time.

The model can manage loops too, through a `loops` tool — including ones created in an earlier
session, since the process table is on disk rather than in the conversation.

## Safety model

Two independent controls:

- **`/mode`** (Shift+Tab cycles) — `cautious` reviews risky actions, `unrestricted` doesn't,
  `plan` authors without building.
- **`/gate`** — a fast local model rates every shell command `none < low < medium < high <
  critical`. The gate is the highest level that auto-runs; anything above it stops for review.
  A hardcoded catastrophic denylist always blocks, regardless of mode or gate.

## Plans

`/megaplan` (alias `/plan`) authors a plan against a shared [MegaPlan](https://github.com/rickmellor/megaplan)
store — research, discuss, then persist — and `/build` executes one. `/work`, `/complete` and
`/uncomplete` operate on individual tasks of the loaded plan, with a picker when you don't
name an id. The prompt shows the loaded plan.

## Context and memory

- **AGENTS.md stack** — folder-scoped instructions for the working directory, always on.
  `/context` shows what's active; `/cd` re-keys the stack, skills and sandbox.
- **Skills** — `/skill <name>` loads a `SKILL.md` playbook into the prompt.
- **Ambient memory** — recall and capture against an [Astoria](https://github.com/rickmellor/astoria)
  memory service, shared with other clients. `/memory` inspects and corrects it: `facts`,
  `remember`, `correct`, `forget`, `history`, `as-of`, `why`.
- **Sessions** — every turn is snapshotted; `/sessions` lists and resumes.
- **MCP** — `/mcp add <name> <url>` (or `-- <cmd>` for stdio). Servers auto-register from
  settings, disabled by default; enable their tools in `/tools`.

## Entry field

A cbreak line reader with bracketed paste, so a pasted multi-line prompt arrives whole and
recalls from history as one entry. Up/down walk history, Tab cycles valid ids at an `<id>`
argument, and the display is wrap- and newline-aware.

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
