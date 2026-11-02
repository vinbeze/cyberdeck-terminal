# cyberpunk-terminal · Cyberdeck

Terminal com cara de monitor CRT para **oh-my-posh**, **ghostty** e **tmux**, mais um banner de "boot".
São quatro *flavors* com os mesmos tokens de cor; trocar de flavor muda só as cores.

| Flavor | Clima | Acento / secundário |
|---|---|---|
| `amber` | o original: monitor âmbar, noite roxa, textura CRT | âmbar / teal |
| `phosphor` | fósforo verde de CRT | verde / âmbar |
| `synth` | neon de fliperama, textura CRT | magenta / ciano |
| `daylight` | versão clara, para o dia | âmbar queimado / teal escuro |

## Instalação

```bash
git clone https://github.com/vinbeze/cyberpunk-terminal.git
cd cyberpunk-terminal && ./install.sh          # ou: ./install.sh synth
```

O instalador copia os temas para `~/.config/cyberdeck/`, instala os comandos em `~/.local/bin/`
e adiciona (uma vez) as linhas que ligam cada programa ao flavor ativo:

| Programa | Linha adicionada |
|---|---|
| bash / zsh | `oh-my-posh init … --config ~/.config/cyberdeck/current/prompt.omp.json` + banner |
| ghostty | `config-file = ?"~/.config/cyberdeck/current/ghostty.conf"` (no fim do `config`) |
| tmux | `source-file -q ~/.config/cyberdeck/current/tmux.conf` (no fim do `tmux.conf`) |

Se você já tem um prompt do oh-my-posh configurado em outro lugar, remova a linha antiga.

## Trocar de flavor

```bash
cyberdeck-flavor            # lista e marca o ativo
cyberdeck-flavor phosphor   # troca
```

O tmux recarrega na hora. No ghostty, `Ctrl+Shift+,` recarrega a config; o prompt muda num shell novo.
O banner pode ser desligado com `CYBERDECK_BANNER=0`.

## Estrutura

```
flavors/palettes.json   fonte única das cores (21 tokens por flavor)
flavors/crt-bg.png      textura CRT do fundo (amber e synth)
build.py                gera themes/ a partir da paleta
themes/<flavor>/        prompt.omp.json · ghostty.conf · tmux.conf · flavor.sh (gerados)
bin/                    cyberdeck-flavor · cyberdeck-banner
```

Para mudar uma cor, edite `flavors/palettes.json` e rode `python3 build.py`.

Requer `oh-my-posh`, uma [Nerd Font](https://www.nerdfonts.com) (CaskaydiaMono) e Python 3 só para o `build.py`.
