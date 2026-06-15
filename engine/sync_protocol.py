#!/usr/bin/env python3
"""
Sincroniza o protocolo canônico (PROTOCOL.md) para dentro de um AGENTS.md.

O protocolo de colaboração é uma CAPACIDADE reusável: nasce em
idea-waddle/PROTOCOL.md (fonte única) e é EMBUTIDO no AGENTS.md de cada
repositório (de caso ou da plataforma), entre marcadores. Assim todo repo é
autossuficiente ao clonar — qualquer agente (Claude, Codex, Gemini…) ou humano
lê o protocolo localmente, sem depender de link remoto.

Uso:
    python engine/sync_protocol.py AGENTS.md             # escreve/atualiza a região
    python engine/sync_protocol.py --check AGENTS.md     # sai 1 se desatualizado (p/ CI)
    python engine/sync_protocol.py --source X.md ALVO    # fonte alternativa

Fonte padrão: <raiz do repo do script>/PROTOCOL.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BEGIN = ("<!-- BEGIN PROTOCOLO (sincronizado de idea-waddle/PROTOCOL.md"
         " — não editar à mão; rode engine/sync_protocol.py) -->")
END = "<!-- END PROTOCOLO -->"


def region(text: str):
    i = text.find(BEGIN)
    j = text.find(END)
    if i == -1 or j == -1 or j < i:
        return None
    return text[i + len(BEGIN):j]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="AGENTS.md a sincronizar")
    ap.add_argument("--check", action="store_true", help="só verifica (exit 1 se drift)")
    ap.add_argument("--source", help="caminho do PROTOCOL.md (default: <repo>/PROTOCOL.md)")
    a = ap.parse_args()

    src = Path(a.source) if a.source else Path(__file__).resolve().parent.parent / "PROTOCOL.md"
    tgt = Path(a.target)
    if not src.exists():
        print(f"PROTOCOL.md não encontrado: {src}")
        return 2
    if not tgt.exists():
        print(f"alvo não encontrado: {tgt}")
        return 2

    protocol = src.read_text(encoding="utf-8").strip()
    want_inner = f"\n\n{protocol}\n\n"
    text = tgt.read_text(encoding="utf-8")
    cur = region(text)

    if a.check:
        if cur is None:
            print(f"✗ {tgt}: marcadores do protocolo ausentes. Rode: python engine/sync_protocol.py {tgt}")
            return 1
        if cur != want_inner:
            print(f"✗ {tgt}: protocolo embutido DESATUALIZADO vs PROTOCOL.md. "
                  f"Rode: python engine/sync_protocol.py {tgt}")
            return 1
        print(f"OK {tgt}: protocolo embutido em dia.")
        return 0

    block = f"{BEGIN}{want_inner}{END}"
    if cur is None:
        new = text.rstrip() + "\n\n" + block + "\n"
    else:
        i = text.find(BEGIN)
        j = text.find(END)
        new = text[:i] + block + text[j + len(END):]
    tgt.write_text(new, encoding="utf-8")
    print(f"protocolo sincronizado em {tgt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
