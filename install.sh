#!/usr/bin/env bash
# Instala o tema cyberpunk do oh-my-posh + banner de boot.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p ~/.config/oh-my-posh ~/.local/bin
cp "$DIR"/oh-my-posh/*.omp.json ~/.config/oh-my-posh/
install -m 755 "$DIR/bin/cyberdeck-banner" ~/.local/bin/cyberdeck-banner

if ! grep -q "cyberpunk.omp.json" ~/.bashrc 2>/dev/null; then
  cat >> ~/.bashrc <<'RC'

# Banner de "boot" do terminal (desative com CYBERDECK_BANNER=0)
command -v cyberdeck-banner &>/dev/null && cyberdeck-banner

# Prompt: oh-my-posh (tema Cyberpunk)
if command -v oh-my-posh &>/dev/null; then
  unset PROMPT_COMMAND
  eval "$(oh-my-posh init bash --config "$HOME/.config/oh-my-posh/cyberpunk.omp.json")"
fi
RC
fi
echo "Pronto! Abra um novo terminal."
