# ArashiOS shell defaults.
export EDITOR=nvim
export VISUAL=nvim
export PAGER=less
export LESS='-FRX'
export PATH="$HOME/.local/bin:$PATH"
export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"

HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_REDUCE_BLANKS
setopt SHARE_HISTORY
setopt AUTO_CD
setopt INTERACTIVE_COMMENTS

autoload -Uz vcs_info
precmd() { vcs_info }
zstyle ':vcs_info:git:*' formats '%F{208}(%b)%f '
setopt PROMPT_SUBST
PROMPT='%F{244}%n@%m%f %F{250}%~%f ${vcs_info_msg_0_}%F{208}%#%f '

if command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh)"
fi
if command -v direnv >/dev/null 2>&1; then
  eval "$(direnv hook zsh)"
fi

if command -v exa >/dev/null 2>&1; then
  alias ls='exa --icons --group-directories-first'
  alias ll='exa -l --icons --group-directories-first'
  alias la='exa -la --icons --group-directories-first'
  alias lt='exa --tree --level=2 --icons'
else
  alias ls='ls --color=auto'
  alias ll='ls -l --color=auto'
  alias la='ls -la --color=auto'
fi

if command -v bat >/dev/null 2>&1; then
  alias cat='bat --paging=never'
fi

alias grep='grep --color=auto'
alias ip='ip -color=auto'
alias ports='ss -tulpn'
alias ..='cd ..'
alias ...='cd ../..'

if [ -f "$HOME/.zshrc.local" ]; then
  source "$HOME/.zshrc.local"
fi
