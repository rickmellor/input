# qchat shell integration — source from ~/.bashrc:  source ~/repos/qchat/qchat-shell.bash
#
#   !task    → qchat goal agent (propose → confirm each step → run → observe)
#   !!task   → qchat autonomous agent (denylist + gemma risk gate; confirms only on risk)
#   Ctrl-G   → generate a command from the current line, drop it in the buffer to edit/run
#
# The ! prefixes rely on history expansion being OFF (set +H) so ! is a literal char.
set +H

command_not_found_handle() {
    local line="$*" ctx
    ctx=$(fc -ln -8 2>/dev/null | sed 's/^[[:space:]]*//')
    case "$line" in
        '!!'*) QCHAT_CTX="$ctx" qchat --auto "${line#!!}"; return $? ;;
        '!'*)  QCHAT_CTX="$ctx" qchat --goal "${line#!}";  return $? ;;
        *)     printf '%s: command not found\n' "$1" >&2;  return 127 ;;
    esac
}

# Ctrl-G: natural language in the line buffer → generated command, editable in place.
# Executes in THIS shell on Enter, so cd/exports/history all behave normally.
_qchat_ctrlg() {
    [ -n "$READLINE_LINE" ] || return
    local gen
    gen=$(QCHAT_CTX="$(fc -ln -8 2>/dev/null)" qchat --gen "$READLINE_LINE" 2>/dev/null) || return
    [ -n "$gen" ] || return
    READLINE_LINE="$gen"
    READLINE_POINT=${#READLINE_LINE}
}
bind -x '"\C-g": _qchat_ctrlg' 2>/dev/null
