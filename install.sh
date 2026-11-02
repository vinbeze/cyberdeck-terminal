#!/usr/bin/env bash
# Instala o Cyberdeck: temas em ~/.config/cyberdeck, comandos em ~/.local/bin,
# e liga oh-my-posh (bash/zsh), ghostty e tmux ao flavor ativo.
#   ./install.sh [flavor]     (padrão: amber, ou o que já estiver ativo)
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
DIR="$HOME/.config/cyberdeck"

mkdir -p "$DIR" ~/.local/bin
rm -rf "$DIR/themes"
cp -r "$REPO/themes" "$DIR/themes"
cp "$REPO/flavors/crt-bg.png" "$DIR/crt-bg.png"
sed -i "s|__CYBERDECK_DIR__|$DIR|g" "$DIR"/themes/*/ghostty.conf
install -m 755 "$REPO/bin/cyberdeck-banner" "$REPO/bin/cyberdeck-flavor" ~/.local/bin/

flavor="${1:-$(cat "$DIR/current/name" 2>/dev/null || echo amber)}"
"$HOME/.local/bin/cyberdeck-flavor" "$flavor" >/dev/null

# add_once <arquivo> <marcador> <bloco>
add_once() {
  [[ -f $1 ]] || return 0
  grep -qF "$2" "$1" && return 0
  printf '\n%s\n' "$3" >> "$1"
  echo "configurado: $1"
}

# strip_block <arquivo> <bloco>: remove a primeira ocorrência exata de um bloco
# (usado para migrar quem instalou a versão antiga, que gravava outras linhas).
strip_block() {
  local file=$1 block=$2 tmp
  [[ -f $file ]] || return 0
  tmp="$(mktemp)"
  if awk 'NR==FNR { b[++n]=$0; next } { a[++m]=$0 }
    END {
      for (i=1; i<=m; i++) {
        hit = (i+n-1 <= m)
        for (j=1; hit && j<=n; j++) if (a[i+j-1] != b[j]) hit=0
        if (hit) { i += n-1; removed=1; continue }
        print a[i]
      }
      exit (removed ? 0 : 1)
    }' <(printf '%s\n' "$block") "$file" > "$tmp"; then
    cat "$tmp" > "$file"
    echo "migrado: $1 (bloco antigo removido)"
  fi
  rm -f "$tmp"
}

# Bloco gravado pela versão anterior do install.sh (marcador: cyberpunk.omp.json).
LEGACY_BASH='# Banner de "boot" do terminal (desative com CYBERDECK_BANNER=0)
command -v cyberdeck-banner &>/dev/null && cyberdeck-banner

# Prompt: oh-my-posh (tema Cyberpunk), no lugar do Starship que o Omarchy carrega.
if command -v oh-my-posh &>/dev/null; then
  unset PROMPT_COMMAND
  eval "$(oh-my-posh init bash --config "$HOME/.config/oh-my-posh/cyberpunk.omp.json")"
fi'

LEGACY_ZSH='# Banner de "boot" do terminal (desative com CYBERDECK_BANNER=0)
command -v cyberdeck-banner &>/dev/null && cyberdeck-banner'

PROMPT='$HOME/.config/cyberdeck/current/prompt.omp.json'
for rc in ~/.bashrc ~/.zshrc; do
  strip_block "$rc" "$LEGACY_BASH"
  strip_block "$rc" "$LEGACY_ZSH"
done
add_once ~/.bashrc "cyberdeck/current/prompt" "# Cyberdeck
command -v cyberdeck-banner &>/dev/null && cyberdeck-banner
if command -v oh-my-posh &>/dev/null; then
  unset PROMPT_COMMAND
  eval \"\$(oh-my-posh init bash --config \"$PROMPT\")\"
fi"
add_once ~/.zshrc "cyberdeck/current/prompt" "# Cyberdeck
(( \$+commands[cyberdeck-banner] )) && cyberdeck-banner
(( \$+commands[oh-my-posh] )) && eval \"\$(oh-my-posh init zsh --config \"$PROMPT\")\""
mkdir -p ~/.config/ghostty ~/.config/tmux
touch ~/.config/ghostty/config ~/.config/tmux/tmux.conf
add_once ~/.config/ghostty/config "cyberdeck/current/ghostty.conf" "# Cyberdeck (deixe no fim do arquivo)
config-file = ?\"~/.config/cyberdeck/current/ghostty.conf\""
add_once ~/.config/tmux/tmux.conf "cyberdeck/current/tmux.conf" "# Cyberdeck (deixe no fim do arquivo)
source-file -q ~/.config/cyberdeck/current/tmux.conf"

echo
echo "Cyberdeck instalado com o flavor '$flavor'. Troque com: cyberdeck-flavor <nome>"
