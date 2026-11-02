#!/usr/bin/env python3
"""Gera os arquivos de cada flavor a partir de flavors/palettes.json.

    python3 build.py

Saída em themes/<flavor>/: prompt.omp.json, ghostty.conf, tmux.conf, flavor.sh.
Os arquivos gerados são versionados; edite a paleta ou este script, nunca eles.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PALETTES = json.loads((ROOT / "flavors" / "palettes.json").read_text())
HEADER = "Gerado por build.py a partir de flavors/palettes.json. Não edite."

# Placeholder trocado pelo install.sh pelo caminho real (o ghostty não expande ~ aqui).
DIR_PLACEHOLDER = "__CYBERDECK_DIR__"


def seg(type_, color, template, **props):
    s = {"type": type_, "style": "plain", "foreground": f"p:{color}", "template": template}
    if props:
        s["properties"] = props
    return s


def prompt(name, c):
    runtime = lambda t, label: seg(t, "muted", f" [ {label} {{{{ .Full }}}} ]", fetch_version=True)
    return {
        "$schema": "https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/schema.json",
        "version": 3,
        "final_space": True,
        "console_title_template": "{{ .Folder }} :: {{ .Shell }}",
        "palette": {k: c[k] for k in ("overlay", "muted", "primary", "secondary", "red")},
        "blocks": [
            {"type": "prompt", "alignment": "left", "segments": [
                seg("text", "overlay", "┌─[ "),
                seg("path", "primary", "{{ .Path }}", style="folder", max_depth=2,
                    folder_separator_icon="/", home_icon="~"),
                # A moldura " ]─[ " fica dentro do segmento git: fora de um repo ela some.
                seg("git", "secondary",
                    "{{ if .Ref }}<p:overlay> ]─[ </>{{ .HEAD }}{{ if .Working.Changed }} {{ .Working.String }}{{ end }}{{ end }}",
                    branch_icon=" ", fetch_status=True, fetch_stash_count=True),
                seg("text", "overlay", " ]"),
                seg("status", "red", " [ ✘ {{ .Code }} ]"),
                seg("executiontime", "muted", " [ {{ .FormattedMs }} ]", threshold=500),
                runtime("go", "go"), runtime("node", "node"), runtime("python", "py"),
            ]},
            {"type": "prompt", "alignment": "right", "segments": [
                seg("time", "muted", "{{ .CurrentDate | date .Format }} ", time_format="15:04"),
            ]},
            {"type": "prompt", "alignment": "left", "newline": True, "segments": [
                {**seg("text", "red", "<b>└─╼</b> "),
                 "foreground_templates": ["{{ if eq .Code 0 }}p:primary{{ end }}"]},
            ]},
        ],
    }


ANSI = ["mantle", "red", "green", "yellow", "blue", "magenta", "cyan", "text",
        "muted", "red-bright", "green-bright", "yellow-bright", "blue-bright",
        "magenta-bright", "cyan-bright", "text"]


def ghostty(name, f):
    c = f["colors"]
    lines = [f"# Cyberdeck · {name} — {f['description']}", f"# {HEADER}", "",
             f"background = {c['base']}", f"foreground = {c['text']}",
             f"cursor-color = {c['primary']}", f"cursor-text = {c['mantle']}",
             "cursor-style = block", "cursor-style-blink = true",
             f"selection-background = {c['primary']}", f"selection-foreground = {c['mantle']}",
             f"bold-color = {c['primary']}", ""]
    lines += [f"palette = {i}={c[k]}" for i, k in enumerate(ANSI)]
    lines += [""]
    if f["crt_background"]:
        lines += ["# Textura de CRT (grid + scanlines + vinheta)",
                  f"background-image = {DIR_PLACEHOLDER}/crt-bg.png",
                  "background-image-opacity = 0.42", "background-image-fit = cover",
                  "background-image-position = center"]
    else:
        lines += ["background-image ="]  # limpa a imagem de um flavor anterior
    lines += ["", "font-family = CaskaydiaMono Nerd Font Mono", "font-size = 11",
              "window-padding-x = 18", "window-padding-y = 16", "window-padding-balance = true",
              "mouse-hide-while-typing = true", "unfocused-split-opacity = 0.85"]
    return "\n".join(lines) + "\n"


def tmux(name, c):
    return f"""# Cyberdeck · {name}
# {HEADER}
set -g status-style "bg={c['mantle']},fg={c['text']}"
set -g status-left "#[fg={c['mantle']},bg={c['primary']},bold] #S #[bg={c['mantle']}] "
set -g status-right "#[fg={c['primary']},bold]#{{?pane_in_mode,COPY ,}}#{{?client_prefix,PREFIX ,}}#{{?window_zoomed_flag,ZOOM ,}}#[fg={c['muted']},nobold]#h "
set -g window-status-format "#[fg={c['muted']}] #I:#W "
set -g window-status-current-format "#[fg={c['secondary']},bold] #I:#W "
set -g pane-border-style "fg={c['overlay']}"
set -g pane-active-border-style "fg={c['primary']}"
set -g message-style "bg={c['mantle']},fg={c['primary']}"
set -g message-command-style "bg={c['mantle']},fg={c['primary']}"
set -g mode-style "bg={c['primary']},fg={c['mantle']}"
setw -g clock-mode-colour "{c['primary']}"
"""


def rgb(h):
    h = h.lstrip("#")
    return ";".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


def flavor_sh(name, c):
    return f"""# Cyberdeck · {name} — cores para scripts (ex.: cyberdeck-banner)
# {HEADER}
CYBERDECK_FLAVOR={name}
CD_PRIMARY='{rgb(c['primary'])}'
CD_SECONDARY='{rgb(c['secondary'])}'
CD_OVERLAY='{rgb(c['overlay'])}'
CD_MUTED='{rgb(c['muted'])}'
"""


def main():
    for name, f in PALETTES.items():
        out = ROOT / "themes" / name
        out.mkdir(parents=True, exist_ok=True)
        c = f["colors"]
        (out / "prompt.omp.json").write_text(json.dumps(prompt(name, c), indent=2, ensure_ascii=False) + "\n")
        (out / "ghostty.conf").write_text(ghostty(name, f))
        (out / "tmux.conf").write_text(tmux(name, c))
        (out / "flavor.sh").write_text(flavor_sh(name, c))
        print(f"themes/{name}/")


if __name__ == "__main__":
    main()
