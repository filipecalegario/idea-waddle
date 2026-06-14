#!/usr/bin/env python3
"""
Motor de consolidação da plataforma idea-waddle.

Lê a caixa morfológica de cada caso (cases/<caso>/morphology/) — parâmetros e
restrições — roda o Cross-Consistency Assessment (CCA) e gera o "site vivo"
em site/. Pensado para rodar localmente e na CI (a cada PR/merge).

Camada atual: Caixa morfológica + CCA. Ganchos (ibis_issue, criteria, arguments)
ficam preservados nos YAML para as camadas futuras (IBIS/QOC/Dung).

Uso:
    pip install pyyaml
    python engine/cca.py
    # abra site/index.html
"""
from __future__ import annotations

import html
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta a dependência PyYAML. Rode: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
CASES_DIR = ROOT / "cases"
SITE_DIR = ROOT / "site"
# Limite de segurança para enumeração do produto cartesiano.
ENUM_LIMIT = 500_000


def load_case(case_dir: Path) -> dict:
    """Carrega parâmetros e restrições de um caso."""
    params = []
    params_dir = case_dir / "morphology" / "params"
    for f in sorted(params_dir.glob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        p = data.get("parameter")
        if p and p.get("options"):
            params.append(p)

    constraints = []
    cfile = case_dir / "morphology" / "constraints.yaml"
    if cfile.exists():
        cdata = yaml.safe_load(cfile.read_text(encoding="utf-8")) or {}
        constraints = cdata.get("constraints", []) or []

    return {"id": case_dir.name, "parameters": params, "constraints": constraints}


def compute_cca(case: dict) -> dict:
    """Roda o CCA: poda configurações que contêm algum par incompatível."""
    params = case["parameters"]
    option_ids = [[o["id"] for o in p["options"]] for p in params]

    total = 1
    for ids in option_ids:
        total *= len(ids)

    # Pares incompatíveis (apenas degree == incompatible podam).
    hard = set()
    weak = []
    for c in case["constraints"]:
        pair = frozenset((c["a"], c["b"]))
        if c.get("degree") == "incompatible":
            hard.add(pair)
        elif c.get("degree") == "weak":
            weak.append(c)

    viable = None
    sample_configs = []
    if total <= ENUM_LIMIT:
        viable = 0
        for combo in itertools.product(*option_ids):
            present = set(combo)
            ok = True
            for pair in hard:
                a, b = tuple(pair)
                if a in present and b in present:
                    ok = False
                    break
            if ok:
                viable += 1
                if len(sample_configs) < 12:
                    sample_configs.append(list(combo))

    quotient = (viable / total) if (viable is not None and total) else None
    return {
        "n_parameters": len(params),
        "total_configs": total,
        "n_hard_constraints": len(hard),
        "n_weak_constraints": len(weak),
        "viable_configs": viable,
        "quotient": quotient,
        "enumerated": viable is not None,
        "sample_configs": sample_configs,
        "weak": weak,
    }


def label_for(case: dict, opt_id: str) -> str:
    for p in case["parameters"]:
        for o in p["options"]:
            if o["id"] == opt_id:
                return o.get("label", opt_id)
    return opt_id


def e(s) -> str:
    return html.escape(str(s))


def render_case_html(case: dict, cca: dict, generated: str) -> str:
    rows = []
    for p in case["parameters"]:
        cells = []
        for o in p["options"]:
            prov = o.get("proposed_by", "?")
            model = o.get("model")
            prov_txt = f"{prov}" + (f" · {model}" if model else "")
            cells.append(
                f'<div class="opt" title="{e(o.get("rationale",""))}">'
                f'<span class="opt-label">{e(o.get("label", o["id"]))}</span>'
                f'<span class="prov">{e(prov_txt)}</span></div>'
            )
        rows.append(
            f'<div class="param"><div class="param-head">{e(p["label"])}</div>'
            f'<div class="opts">{"".join(cells)}</div></div>'
        )

    constraints_html = []
    for c in case["constraints"]:
        badge = c.get("degree", "")
        cls = "hard" if badge == "incompatible" else "weak"
        constraints_html.append(
            f'<li class="{cls}"><span class="badge {cls}">{e(badge)}</span> '
            f'<span class="ctype">{e(c.get("type",""))}</span> — '
            f'<b>{e(label_for(case, c["a"]))}</b> ✕ <b>{e(label_for(case, c["b"]))}</b>'
            f'<br><small>{e(c.get("note",""))} '
            f'<i>({e(c.get("by","?"))}{(" · " + e(c["model"])) if c.get("model") else ""})</i></small></li>'
        )

    q = cca["quotient"]
    q_txt = f"{q*100:.1f}%" if q is not None else "—"
    viable_txt = f'{cca["viable_configs"]:,}' if cca["enumerated"] else "não enumerado (espaço grande)"

    samples = ""
    if cca["sample_configs"]:
        items = []
        for combo in cca["sample_configs"]:
            labels = " · ".join(label_for(case, x) for x in combo)
            items.append(f"<li>{e(labels)}</li>")
        samples = (
            '<h2>Amostra de configurações viáveis</h2>'
            f'<ol class="samples">{"".join(items)}</ol>'
        )

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>idea-waddle — {e(case["id"])}</title>
<style>
  :root {{ --bg:#0f1117; --card:#1a1d27; --line:#2a2e3c; --txt:#e6e8ee; --mut:#9aa0b0; --acc:#7aa2f7; --hard:#f7768e; --weak:#e0af68; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--txt); font:15px/1.5 system-ui,sans-serif; }}
  .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  .sub {{ color:var(--mut); margin-bottom:20px; }}
  .stats {{ display:flex; flex-wrap:wrap; gap:12px; margin:16px 0 28px; }}
  .stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 16px; min-width:130px; }}
  .stat b {{ display:block; font-size:22px; color:var(--acc); }}
  .stat span {{ color:var(--mut); font-size:12px; }}
  h2 {{ font-size:16px; margin:28px 0 10px; border-bottom:1px solid var(--line); padding-bottom:6px; }}
  .box {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; }}
  .param {{ background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; }}
  .param-head {{ background:#222633; padding:8px 12px; font-weight:600; font-size:13px; }}
  .opts {{ padding:8px; display:flex; flex-direction:column; gap:6px; }}
  .opt {{ background:#12151d; border:1px solid var(--line); border-radius:7px; padding:7px 9px; }}
  .opt-label {{ display:block; font-size:13px; }}
  .prov {{ display:block; color:var(--mut); font-size:11px; margin-top:2px; }}
  ul.cons {{ list-style:none; padding:0; }}
  ul.cons li {{ background:var(--card); border:1px solid var(--line); border-left:3px solid var(--line); border-radius:8px; padding:9px 12px; margin-bottom:8px; }}
  ul.cons li.hard {{ border-left-color:var(--hard); }}
  ul.cons li.weak {{ border-left-color:var(--weak); }}
  .badge {{ font-size:11px; padding:1px 7px; border-radius:20px; }}
  .badge.hard {{ background:rgba(247,118,142,.18); color:var(--hard); }}
  .badge.weak {{ background:rgba(224,175,104,.18); color:var(--weak); }}
  .ctype {{ color:var(--mut); font-size:12px; }}
  .samples li, .cons small {{ color:var(--mut); }}
  footer {{ color:var(--mut); font-size:12px; margin-top:32px; border-top:1px solid var(--line); padding-top:12px; }}
  a {{ color:var(--acc); }}
</style></head>
<body><div class="wrap">
  <h1>Caixa morfológica viva — {e(case["id"])}</h1>
  <div class="sub">Plataforma <b>idea-waddle</b> · colaboração criativa humano + agente sobre Git ·
    gerado em {e(generated)}</div>

  <div class="stats">
    <div class="stat"><b>{cca["n_parameters"]}</b><span>parâmetros</span></div>
    <div class="stat"><b>{cca["total_configs"]:,}</b><span>configurações totais</span></div>
    <div class="stat"><b>{cca["n_hard_constraints"]}</b><span>restrições (poda)</span></div>
    <div class="stat"><b>{viable_txt}</b><span>configurações viáveis</span></div>
    <div class="stat"><b>{q_txt}</b><span>espaço de solução</span></div>
  </div>

  <h2>Parâmetros &amp; opções</h2>
  <div class="box">{"".join(rows)}</div>

  <h2>Restrições de consistência (CCA)</h2>
  <ul class="cons">{"".join(constraints_html) or "<li>Nenhuma restrição ainda.</li>"}</ul>

  {samples}

  <footer>
    Proveniência registrada por opção/restrição (quem · qual modelo). Diversidade é princípio do projeto —
    veja <a href="https://github.com">o repositório</a>, o <code>AGENTS.md</code> e <code>docs/discovery/</code>.
    Restrições <span class="badge weak">weak</span> alertam mas não podam.
  </footer>
</div></body></html>"""


def render_index(cases: list[dict]) -> str:
    items = "".join(
        f'<li><a href="{e(c["id"])}/index.html">{e(c["id"])}</a></li>' for c in cases
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>idea-waddle</title>
<style>body{{margin:0;background:#0f1117;color:#e6e8ee;font:16px/1.6 system-ui,sans-serif}}
.wrap{{max-width:760px;margin:0 auto;padding:40px 24px}}a{{color:#7aa2f7}}
li{{margin:8px 0}}</style></head>
<body><div class="wrap">
<h1>idea-waddle</h1>
<p>Plataforma de colaboração criativa entre humanos e agentes de IA, usando o Git como espinha dorsal.</p>
<h2>Casos</h2><ul>{items}</ul>
</div></body></html>"""


def main() -> int:
    SITE_DIR.mkdir(exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    cases = []
    if CASES_DIR.exists():
        for case_dir in sorted(CASES_DIR.iterdir()):
            if (case_dir / "morphology" / "params").is_dir():
                cases.append(case_dir)

    if not cases:
        print("Nenhum caso com morphology/params encontrado.")
        return 1

    loaded = []
    for case_dir in cases:
        case = load_case(case_dir)
        cca = compute_cca(case)
        loaded.append(case)

        out_dir = SITE_DIR / case["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            render_case_html(case, cca, generated), encoding="utf-8"
        )
        (out_dir / "data.json").write_text(
            json.dumps({"case": case, "cca": cca}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(
            f"[{case['id']}] {cca['n_parameters']} params · "
            f"{cca['total_configs']:,} totais · "
            f"{cca['viable_configs']} viáveis "
            f"({(cca['quotient'] or 0)*100:.1f}%) · "
            f"{cca['n_hard_constraints']} restrições"
        )

    (SITE_DIR / "index.html").write_text(render_index(loaded), encoding="utf-8")
    print(f"Site gerado em {SITE_DIR}/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
