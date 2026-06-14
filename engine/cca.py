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

Variáveis de ambiente (opcionais, p/ consumir casos de um repo externo):
    IW_CASES    diretório com os casos (default: <repo>/cases)
    IW_SITE     diretório de saída do site (default: <repo>/site)
    IW_CASE     um único diretório de caso (morphology/ na raiz); ignora IW_CASES
    IW_CASE_ID  id/nome do caso (default: nome do diretório)
"""
from __future__ import annotations

import html
import itertools
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta a dependência PyYAML. Rode: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
# Origem dos casos e destino do site são configuráveis por ambiente, para que o
# motor possa ser consumido por um repositório de caso externo (ver docs/spec).
# Sem as variáveis, o comportamento é o padrão (cases/ e site/ deste repo).
CASES_DIR = Path(os.environ.get("IW_CASES", ROOT / "cases"))
SITE_DIR = Path(os.environ.get("IW_SITE", ROOT / "site"))
# Limite de segurança para enumeração do produto cartesiano.
ENUM_LIMIT = 2_000_000


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

    criteria = []
    crfile = case_dir / "morphology" / "criteria.yaml"
    if crfile.exists():
        crdata = yaml.safe_load(crfile.read_text(encoding="utf-8")) or {}
        criteria = crdata.get("criteria", []) or []

    assumptions = {}
    afile = case_dir / "morphology" / "assumptions.yaml"
    if afile.exists():
        adata = yaml.safe_load(afile.read_text(encoding="utf-8")) or {}
        assumptions = adata.get("assumptions", {}) or {}

    arguments = []
    argfile = case_dir / "morphology" / "arguments.yaml"
    if argfile.exists():
        argdata = yaml.safe_load(argfile.read_text(encoding="utf-8")) or {}
        arguments = argdata.get("arguments", []) or []

    return {
        "id": case_dir.resolve().name,
        "parameters": params,
        "constraints": constraints,
        "criteria": criteria,
        "assumptions": assumptions,
        "arguments": arguments,
    }


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


def grounded_extension(arguments: list) -> dict:
    """Semântica 'grounded' de Dung: rotula cada argumento como aceito/derrotado/
    indeciso a partir das relações de ataque. Retorna {arg_id: 'in'|'out'|'undecided'}."""
    ids = [a["id"] for a in arguments if a.get("id")]
    idset = set(ids)
    # attackers[b] = conjunto de a que atacam b
    attackers = {i: set() for i in ids}
    for a in arguments:
        src = a.get("id")
        for tgt in a.get("attacks", []) or []:
            if tgt in idset and src in idset:
                attackers[tgt].add(src)

    label = {}  # in | out
    changed = True
    while changed:
        changed = False
        for i in ids:
            if i in label:
                continue
            atks = attackers[i]
            if all(x in label and label[x] == "out" for x in atks):
                label[i] = "in"
                changed = True
            elif any(x in label and label[x] == "in" for x in atks):
                label[i] = "out"
                changed = True
    return {i: label.get(i, "undecided") for i in ids}


def label_for(case: dict, opt_id: str) -> str:
    for p in case["parameters"]:
        for o in p["options"]:
            if o["id"] == opt_id:
                return o.get("label", opt_id)
    return opt_id


def e(s) -> str:
    return html.escape(str(s))


CASE_TEMPLATE = r"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>idea-waddle — __CASE_ID__</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;0,9..144,700;1,9..144,400&family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --paper:#ece4d3; --paper-2:#e2d8c2; --panel:#f2ecdf; --ink:#1b1812; --ink-2:#544d3f;
    --rule:rgba(27,24,18,.15); --rule-2:rgba(27,24,18,.45);
    --signal:#bf3a1d; --blue:#234a63; --ok:#5e6a2b; --ochre:#9a6a12; --hatch:rgba(191,58,29,.13);
    --disp:'Fraunces',Georgia,'Times New Roman',serif;
    --body:'Archivo',system-ui,sans-serif;
    --mono:'IBM Plex Mono',ui-monospace,'Courier New',monospace;
  }
  * { box-sizing:border-box; }
  html { -webkit-text-size-adjust:100%; }
  body {
    margin:0; color:var(--ink); font-family:var(--body); font-size:15px; line-height:1.55;
    background-color:var(--paper);
    background-image:linear-gradient(var(--rule) 1px,transparent 1px),
                     linear-gradient(90deg,var(--rule) 1px,transparent 1px);
    background-size:30px 30px; background-position:-1px -1px;
  }
  body::before {
    content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.05; mix-blend-mode:multiply;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  ::selection { background:var(--signal); color:var(--paper); }
  .topbar { position:fixed; top:0; left:0; right:0; height:5px; background:var(--signal); z-index:30; }
  .wrap { position:relative; z-index:1; max-width:1120px; margin:0 auto; padding:40px 28px 84px; counter-reset:sec; }
  a { color:var(--blue); text-underline-offset:3px; }
  code { font-family:var(--mono); font-size:.86em; background:var(--paper-2); padding:1px 5px; }

  /* cabeçalho (masthead) */
  .masthead { animation:rise .6s both; }
  .dateline-row { display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap;
    font-family:var(--mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--ink-2); }
  .title { font-family:var(--disp); font-weight:600; font-size:clamp(44px,9vw,86px); line-height:.9;
    letter-spacing:-.025em; margin:.16em 0 .12em; }
  .title .dot { color:var(--signal); }
  .standfirst { font-family:var(--disp); font-style:italic; font-weight:400; font-size:clamp(16px,2.5vw,22px);
    color:var(--ink-2); max-width:48ch; margin:0; }
  .rule-d { border:0; border-top:1px solid var(--rule-2); box-shadow:0 3px 0 -2px var(--rule-2); margin:20px 0 0; }

  /* faixa de indicadores */
  .readout { display:flex; flex-wrap:wrap; margin:24px 0 28px; border:1px solid var(--rule-2);
    background:var(--panel); animation:rise .6s .08s both; }
  .metric { flex:1 1 0; min-width:118px; padding:14px 16px; border-right:1px solid var(--rule); }
  .metric:last-child { border-right:0; }
  .metric .mv { font-family:var(--disp); font-weight:600; font-size:30px; line-height:1; font-variant-numeric:tabular-nums; }
  .metric.accent .mv { color:var(--signal); }
  .metric .ml { display:block; margin-top:7px; font-family:var(--mono); font-size:10px; letter-spacing:.13em;
    text-transform:uppercase; color:var(--ink-2); }

  /* instrumento (estimativas), fixo no topo */
  .instrument { position:sticky; top:14px; z-index:8; background:var(--panel); border:1.5px solid var(--ink);
    padding:16px 18px; margin:0 0 30px; box-shadow:7px 7px 0 var(--rule-2); animation:rise .6s .16s both; }
  .instrument::before, .instrument::after { content:""; position:absolute; width:11px; height:11px; }
  .instrument::before { top:-1px; left:-1px; border-top:2px solid var(--signal); border-left:2px solid var(--signal); }
  .instrument::after { bottom:-1px; right:-1px; border-bottom:2px solid var(--signal); border-right:2px solid var(--signal); }
  .instrument .ihead { display:flex; justify-content:space-between; align-items:baseline; gap:12px; margin-bottom:13px; }
  .instrument h2 { font-family:var(--disp); font-weight:600; font-size:19px; margin:0; }
  .note { font-family:var(--mono); font-size:11.5px; color:var(--ink-2); }

  .est-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(148px,1fr)); gap:1px;
    background:var(--rule); border:1px solid var(--rule); }
  .est { background:var(--panel); padding:11px 14px; }
  .est .k { font-family:var(--mono); font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-2); }
  .est .v { font-family:var(--disp); font-weight:600; font-size:23px; line-height:1.1; margin-top:4px;
    font-variant-numeric:tabular-nums; animation:tick .4s ease; }
  .est .v .u { font-family:var(--mono); font-weight:400; font-size:12px; color:var(--ink-2); }
  .est .miss { font-family:var(--mono); font-size:11px; color:var(--ink-2); margin-top:7px; }
  .gauge { display:flex; gap:3px; margin-top:9px; }
  .gauge span { flex:1; height:9px; background:var(--rule); }
  .gauge span.on { background:var(--ok); }
  .est .qv { font-family:var(--mono); font-size:11px; color:var(--ink-2); margin-top:5px; }

  /* títulos de seção numerados */
  .sec { display:flex; align-items:baseline; gap:12px; margin:38px 0 10px; counter-increment:sec; }
  .sec .no { font-family:var(--mono); font-size:12px; color:var(--signal); letter-spacing:.06em; }
  .sec .no::before { content:"§" counter(sec,decimal-leading-zero); }
  .sec h2 { font-family:var(--disp); font-weight:600; font-size:22px; margin:0; letter-spacing:-.01em; }
  .sec .line { flex:1; border-top:1px solid var(--rule); align-self:center; }
  .lead { color:var(--ink-2); font-size:14px; margin:0 0 16px; max-width:78ch; }

  /* caixa morfológica (padrão GMA: linha = parâmetro) */
  .gma { border:1.5px solid var(--ink); background:var(--panel); counter-reset:row;
    box-shadow:7px 7px 0 var(--rule-2); }
  .row { display:grid; grid-template-columns:226px 1fr; border-top:1px solid var(--rule);
    counter-increment:row; animation:rise .5s both; animation-delay:calc(var(--i,0)*55ms); }
  .row:first-child { border-top:0; }
  .row-label { padding:14px 16px; border-right:1px solid var(--rule); }
  .row-label .rl-no { font-family:var(--mono); font-size:11px; color:var(--signal); letter-spacing:.08em; }
  .row-label .rl-no::before { content:"§" counter(row,decimal-leading-zero); }
  .row-label .rl-name { display:block; font-family:var(--disp); font-weight:600; font-size:16px; line-height:1.15; margin-top:3px; }
  .row-label .rl-desc { display:block; font-size:11.5px; color:var(--ink-2); margin-top:6px; line-height:1.35; }
  .row-cells { display:flex; flex-wrap:wrap; gap:8px; padding:12px; align-content:flex-start; }
  .opt { position:relative; flex:1 1 162px; min-width:150px; padding:10px 12px; background:var(--paper);
    border:1px solid var(--rule-2); cursor:pointer; user-select:none;
    transition:transform .12s, box-shadow .12s, background .12s, color .12s; }
  .opt:hover { transform:translate(-2px,-2px); box-shadow:3px 3px 0 var(--ink); }
  .opt .ol { display:block; font-family:var(--mono); font-size:12.5px; font-weight:500; line-height:1.3; padding-right:14px; }
  .opt .op { display:block; margin-top:7px; font-family:var(--mono); font-size:9.5px; letter-spacing:.06em;
    text-transform:uppercase; color:var(--ink-2); }
  .opt.selected { background:var(--ink); color:var(--paper); border-color:var(--ink); box-shadow:3px 3px 0 var(--signal); }
  .opt.selected .op { color:rgba(236,228,211,.66); }
  .opt.selected::after { content:"\25CF"; position:absolute; top:9px; right:10px; color:var(--signal); font-size:9px; }
  .opt.blocked { cursor:not-allowed; color:var(--signal); border-style:dashed; border-color:var(--signal);
    background-image:repeating-linear-gradient(45deg,transparent 0 6px,var(--hatch) 6px 7px); }
  .opt.blocked .ol { text-decoration:line-through; }
  .opt.blocked:hover { transform:none; box-shadow:none; }
  .opt.warn { border-color:var(--ochre); }
  .opt.warn::after { content:"!"; position:absolute; top:7px; right:11px; color:var(--ochre); font-family:var(--disp); font-weight:700; }
  .opt.flash { animation:nope .4s; }

  /* livros-razão (seleção / restrições) */
  .panels { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:18px; }
  .ledger { background:var(--panel); border:1px solid var(--rule-2); padding:16px 18px; }
  .ledger h3 { font-family:var(--disp); font-weight:600; font-size:15px; margin:0 0 13px;
    display:flex; justify-content:space-between; align-items:center; gap:10px; }
  .empty { font-family:var(--mono); font-size:12px; color:var(--ink-2); }
  .selitem { padding:8px 0 8px 14px; border-left:2px solid var(--ink); margin-bottom:13px; }
  .selitem .p { font-family:var(--mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--signal); }
  .selitem .l { font-family:var(--disp); font-weight:500; font-size:15px; margin-top:2px; }
  .selitem .r { font-size:12.5px; color:var(--ink-2); margin-top:3px; }
  .selitem .by { font-family:var(--mono); font-size:10px; color:var(--ink-2); margin-top:4px; }
  .space { margin-top:10px; padding-top:10px; border-top:1px dashed var(--rule-2);
    font-family:var(--mono); font-size:12px; color:var(--ink-2); }
  .space b { font-family:var(--disp); font-size:18px; color:var(--signal); }
  .cline { padding:8px 0 8px 12px; border-left:2px solid var(--rule-2); margin-bottom:11px; font-size:13px; }
  .cline.hard { border-left-color:var(--signal); }
  .cline.weak { border-left-color:var(--ochre); }
  .cline small { display:block; color:var(--ink-2); margin-top:3px; }
  .badge { font-family:var(--mono); font-size:10px; letter-spacing:.06em; text-transform:uppercase;
    padding:1px 6px; border:1px solid currentColor; }
  .badge.hard { color:var(--signal); }
  .badge.weak { color:var(--ochre); }
  .ctype { font-family:var(--mono); font-size:11px; color:var(--ink-2); }
  .btn { font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    background:transparent; color:var(--ink); border:1px solid var(--ink); padding:5px 11px; cursor:pointer; }
  .btn:hover { background:var(--ink); color:var(--paper); }

  /* listas de referência */
  ul.cons { list-style:none; padding:0; margin:0; border:1px solid var(--rule-2); background:var(--panel); }
  ul.cons li { padding:11px 14px; border-top:1px solid var(--rule); font-size:13px; }
  ul.cons li:first-child { border-top:0; }
  ul.cons li.hard { box-shadow:inset 3px 0 0 var(--signal); }
  ul.cons li.weak { box-shadow:inset 3px 0 0 var(--ochre); }
  ul.cons b { font-family:var(--disp); font-weight:600; }
  ul.cons small { color:var(--ink-2); }
  .badge.ok { color:var(--ok); }
  .layer { font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--ink-2); border:1px solid var(--rule-2); padding:1px 7px; margin-left:8px; vertical-align:middle; }

  /* IBIS + argumentação */
  .ibis { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }
  .issue { background:var(--panel); border:1px solid var(--rule-2); padding:14px 16px; }
  .issue-q { font-family:var(--disp); font-weight:600; font-size:15px; margin-bottom:10px;
    padding-bottom:8px; border-bottom:1px solid var(--rule); }
  .arg { border-left:2px solid var(--rule-2); padding:7px 0 9px 12px; margin-bottom:10px; }
  .arg.ok { border-left-color:var(--ok); }
  .arg.hard { border-left-color:var(--signal); }
  .arg.weak { border-left-color:var(--ochre); }
  .arg .stance { font-family:var(--mono); font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--ink-2); }
  .arg .claim { font-size:13.5px; margin-top:5px; }
  .arg.hard .claim { text-decoration:line-through; opacity:.7; }
  .arg .arg-ref { font-family:var(--mono); font-size:10.5px; color:var(--signal); margin-top:4px; }
  .arg .arg-by { font-family:var(--mono); font-size:10px; color:var(--ink-2); margin-top:4px; }

  /* matriz QOC */
  .qoc-wrap { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }
  .qoc-block { background:var(--panel); border:1px solid var(--rule-2); padding:12px 14px; }
  .qoc-p { font-family:var(--disp); font-weight:600; font-size:14px; margin-bottom:8px; }
  table.qoc { width:100%; border-collapse:collapse; font-size:12.5px; }
  table.qoc th { font-family:var(--mono); font-size:10px; letter-spacing:.05em; text-transform:uppercase;
    color:var(--ink-2); text-align:center; font-weight:400; padding:3px 4px; border-bottom:1px solid var(--rule); }
  table.qoc th:first-child { text-align:left; }
  table.qoc td { padding:5px 4px; border-bottom:1px solid var(--rule); }
  table.qoc td.opt-name { font-family:var(--mono); font-size:11px; }
  table.qoc td.sc { text-align:center; font-family:var(--disp); font-weight:600; font-variant-numeric:tabular-nums; }
  table.qoc td.sc.na { color:var(--rule-2); font-weight:400; }

  footer { margin-top:48px; padding-top:18px; border-top:1px solid var(--rule-2);
    font-family:var(--mono); font-size:11.5px; letter-spacing:.02em; color:var(--ink-2); line-height:1.8; }
  footer code { color:var(--ink); }

  @keyframes rise { from { opacity:0; transform:translateY(9px); } to { opacity:1; transform:none; } }
  @keyframes tick { from { opacity:.25; transform:translateY(3px); } to { opacity:1; transform:none; } }
  @keyframes nope { 0%,100%{transform:none;} 25%{transform:translateX(-3px);} 75%{transform:translateX(3px);} }

  @media (max-width:780px) {
    .panels { grid-template-columns:1fr; }
    .row { grid-template-columns:1fr; }
    .row-label { border-right:0; border-bottom:1px solid var(--rule); }
    .instrument { position:static; }
  }
  @media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
</style></head>
<body>
<div class="topbar"></div>
<div class="wrap">
  <header class="masthead">
    <div class="dateline-row"><span>Caso · __CASE_ID__</span><span>Revisão · __GENERATED__</span></div>
    <h1 class="title">idea<span class="dot">·</span>waddle</h1>
    <p class="standfirst">Caixa morfológica viva — análise colaborativa entre humanos e agentes, versionada sobre Git.</p>
    <hr class="rule-d">
  </header>

  <section class="readout">
    <div class="metric"><span class="mv">__N_PARAMS__</span><span class="ml">parâmetros</span></div>
    <div class="metric"><span class="mv">__TOTAL__</span><span class="ml">config. totais</span></div>
    <div class="metric"><span class="mv">__N_HARD__</span><span class="ml">restrições</span></div>
    <div class="metric accent"><span class="mv">__VIABLE__</span><span class="ml">config. viáveis</span></div>
    <div class="metric"><span class="mv">__QUOTIENT__</span><span class="ml">espaço de solução</span></div>
  </section>

  <section class="instrument">
    <div class="ihead"><h2>Leitura da configuração</h2><span class="note">atualiza com a seleção &#8595;</span></div>
    <div id="estimates"><div class="empty">Selecione opções na caixa abaixo para estimar custo, potência e energia.</div></div>
    <p class="note" style="margin:13px 0 0">Valores são placeholders a refinar — premissas em
      <code>assumptions.yaml</code>, dados por opção em <code>params/*.yaml</code>. Tratar como ordem de grandeza.</p>
  </section>

  <div class="sec"><span class="no"></span><h2>Caixa morfológica</h2><span class="line"></span></div>
  <p class="lead">Clique numa célula por linha para montar uma configuração. Opções
    <b style="color:var(--signal)">incompatíveis</b> com a seleção ficam bloqueadas; as de
    <b style="color:var(--ochre)">alerta</b> seguem disponíveis. Cada escolha revela comentário, proveniência e caminhos de restrição.</p>
  <div class="gma" id="gma">__ROWS__</div>

  <div class="panels">
    <div class="ledger">
      <h3>Seleção atual <button class="btn" id="clear">Limpar</button></h3>
      <div id="selection"><div class="empty">Nenhuma célula selecionada.</div></div>
      <div class="space" id="space"></div>
    </div>
    <div class="ledger">
      <h3>Caminhos de restrição</h3>
      <div id="restrictions"><div class="empty">Selecione células para ver as restrições disparadas.</div></div>
    </div>
  </div>

  <div class="sec"><span class="no"></span><h2>Critérios de avaliação</h2><span class="line"></span></div>
  <ul class="cons">__CRITERIA__</ul>
  <p class="note" style="margin:10px 0 0">Premissas (placeholders, em <code>assumptions.yaml</code>): __ASSUMPTIONS__</p>

  <div class="sec"><span class="no"></span><h2>Matriz QOC <span class="layer">opções × critérios</span></h2><span class="line"></span></div>
  <div class="qoc-wrap">__QOCMATRIX__</div>

  <div class="sec"><span class="no"></span><h2>Discussão &amp; argumentação <span class="layer">IBIS · Dung</span></h2><span class="line"></span></div>
  <p class="lead">Argumentos pró/contra cada opção (camada IBIS). Setas de refutação formam um grafo; o motor calcula a <b>semântica grounded</b> (Dung) — quais argumentos sobrevivem ao debate. __IBIS_SUMMARY__</p>
  <div class="ibis">__IBIS__</div>

  <div class="sec"><span class="no"></span><h2>Restrições registradas</h2><span class="line"></span></div>
  <ul class="cons">__CONS__</ul>

  <footer>
    idea·waddle — colaboração criativa humano + agente sobre Git.<br>
    Proveniência registrada por opção e restrição (quem · qual modelo). Diversidade é princípio do projeto.<br>
    Consulte <code>README.md</code> · <code>AGENTS.md</code> · <code>docs/discovery/</code> · <code>docs/spec/</code>.
  </footer>
</div>
<script>
const DATA = __DATA_JSON__;
// índices auxiliares
const OPT = {};            // optId -> {label, rationale, by, model, param, paramLabel}
DATA.params.forEach(function(p){
  p.options.forEach(function(o){
    OPT[o.id] = {label:o.label, rationale:o.rationale, by:o.by, model:o.model,
                 param:p.id, paramLabel:p.label, estimates:o.estimates||{}, scores:o.scores||{}};
  });
});
function findConstraint(x, y){
  for (var i=0;i<DATA.constraints.length;i++){
    var c = DATA.constraints[i];
    if ((c.a===x && c.b===y) || (c.a===y && c.b===x)) return c;
  }
  return null;
}
const selected = {};       // paramId -> optId

function hardFree(ids){
  for (var i=0;i<DATA.constraints.length;i++){
    var c = DATA.constraints[i];
    if (c.degree==='incompatible' && ids.indexOf(c.a)>-1 && ids.indexOf(c.b)>-1) return false;
  }
  return true;
}
function countViable(partial){
  var ps = DATA.params, count = 0;
  function rec(i, chosen){
    if (i===ps.length){ if (hardFree(chosen)) count++; return; }
    var p = ps[i];
    if (partial[p.id]) rec(i+1, chosen.concat(partial[p.id]));
    else p.options.forEach(function(o){ rec(i+1, chosen.concat(o.id)); });
  }
  rec(0, []);
  return count;
}

function recompute(){
  var selIds = Object.keys(selected).map(function(k){ return selected[k]; });
  document.querySelectorAll('.opt').forEach(function(el){
    var id = el.dataset.opt, p = el.dataset.param;
    el.classList.remove('selected','blocked','warn');
    if (selected[p]===id){ el.classList.add('selected'); return; }
    var blocked=false, warn=false;
    for (var i=0;i<selIds.length;i++){
      var s = selIds[i];
      if (OPT[s].param===p) continue;            // mesma linha não conflita
      var c = findConstraint(id, s);
      if (c && c.degree==='incompatible'){ blocked=true; break; }
      if (c && c.degree==='weak') warn=true;
    }
    if (blocked) el.classList.add('blocked');
    else if (warn) el.classList.add('warn');
  });
  renderSelection(selIds);
  renderRestrictions(selIds);
  renderSpace();
  renderEstimates();
}

// ---- camada QOC: estimativas de custo/energia + escores ----
function critById(id){
  for (var i=0;i<DATA.criteria.length;i++){ if (DATA.criteria[i].id===id) return DATA.criteria[i]; }
  return {};
}
function aggScore(id, vals){
  if (!vals || !vals.length) return null;
  var agg = (critById(id).aggregation) || 'min';
  if (agg==='avg') return vals.reduce(function(a,b){return a+b;},0)/vals.length;
  if (agg==='sum') return vals.reduce(function(a,b){return a+b;},0);
  return Math.min.apply(null, vals);
}
function computeEstimates(){
  var A = DATA.assumptions || {};
  var gpus=null, capexPerGpu=null, tdp=null, capexFixed=0;
  var scoreAgg = {};
  Object.keys(selected).forEach(function(pid){
    var o = OPT[selected[pid]], est = o.estimates||{}, sc = o.scores||{};
    if (est.n_gpus!=null) gpus = est.n_gpus;
    if (est.capex_per_gpu_brl!=null) capexPerGpu = est.capex_per_gpu_brl;
    if (est.tdp_w_per_gpu!=null) tdp = est.tdp_w_per_gpu;
    if (est.capex_fixed_brl!=null) capexFixed += est.capex_fixed_brl;
    Object.keys(sc).forEach(function(k){ (scoreAgg[k]=scoreAgg[k]||[]).push(sc[k]); });
  });
  var capex = (gpus!=null && capexPerGpu!=null) ? gpus*capexPerGpu + capexFixed : null;
  var powerKw = (gpus!=null && tdp!=null && A.pue!=null) ? gpus*tdp/1000*A.pue : null;
  var energy = (powerKw!=null && A.hours_per_month!=null && A.tariff_brl_per_kwh!=null)
      ? powerKw*A.hours_per_month*A.tariff_brl_per_kwh : null;
  return {gpus:gpus, capex:capex, powerKw:powerKw, energy:energy, scoreAgg:scoreAgg};
}
function fmtBRL(n){ return 'R$ ' + Math.round(n).toLocaleString('pt-BR'); }
function quantCard(k, valHtml, miss){
  var inner = valHtml ? '<div class="v">'+valHtml+'</div>' : '<div class="miss">'+ (miss||'sem dado') +'</div>';
  return '<div class="est quant"><div class="k">'+esc(k)+'</div>'+inner+'</div>';
}
function gauge(v){
  var s=''; var on=Math.round(v);
  for (var i=1;i<=5;i++){ s += '<span class="'+(i<=on?'on':'')+'"></span>'; }
  return '<div class="gauge">'+s+'</div>';
}
function qualCard(k, v){
  if (v==null) return '<div class="est qual"><div class="k">'+esc(k)+'</div><div class="miss">sem dado</div></div>';
  return '<div class="est qual"><div class="k">'+esc(k)+'</div>'+gauge(v)+
         '<div class="qv">'+ (Math.round(v*10)/10) +' / 5</div></div>';
}
function renderEstimates(){
  var box = document.getElementById('estimates');
  if (!Object.keys(selected).length){
    box.innerHTML = '<div class="empty">Selecione opções para estimar custo, potência e energia.</div>'; return;
  }
  var E = computeEstimates(), cards = [];
  cards.push(quantCard('Total de GPUs', E.gpus!=null ? E.gpus.toLocaleString('pt-BR') : null, 'selecione a escala'));
  cards.push(quantCard('Custo de capital', E.capex!=null ? fmtBRL(E.capex) : null, 'hardware + escala'));
  cards.push(quantCard('Potência', E.powerKw!=null ? (Math.round(E.powerKw*10)/10)+' kW' : null, 'selecione hardware + escala'));
  cards.push(quantCard('Energia', E.energy!=null ? (fmtBRL(E.energy)+'/mês') : null, 'depende da potência'));
  var wsum=0, wtot=0;
  DATA.criteria.filter(function(c){ return c.kind==='qualitative'; }).forEach(function(c){
    var v = aggScore(c.id, E.scoreAgg[c.id]);
    cards.push(qualCard(c.label, v));
    if (v!=null){ var w=c.weight||1; wsum+=v*w; wtot+=w; }
  });
  if (wtot>0){ cards.push(qualCard('Índice QOC (ponderado)', wsum/wtot)); }
  box.innerHTML = '<div class="est-grid">'+cards.join('')+'</div>';
}

function renderSelection(selIds){
  var box = document.getElementById('selection');
  if (!selIds.length){ box.innerHTML = '<div class="empty">Nenhuma célula selecionada.</div>'; return; }
  box.innerHTML = DATA.params.filter(function(p){ return selected[p.id]; }).map(function(p){
    var o = OPT[selected[p.id]];
    var by = o.by ? (o.by + (o.model ? ' · ' + o.model : '')) : '';
    return '<div class="selitem"><div class="p">'+esc(p.label)+'</div>'+
           '<div class="l">'+esc(o.label)+'</div>'+
           (o.rationale ? '<div class="r">'+esc(o.rationale)+'</div>' : '')+
           (by ? '<div class="by">'+esc(by)+'</div>' : '')+'</div>';
  }).join('');
}

function renderRestrictions(selIds){
  var box = document.getElementById('restrictions');
  var lines = [];
  DATA.constraints.forEach(function(c){
    var aSel = selIds.indexOf(c.a)>-1, bSel = selIds.indexOf(c.b)>-1;
    if (!aSel && !bSel) return;                  // só mostra restrições tocadas pela seleção
    var cls = c.degree==='incompatible' ? 'hard' : 'weak';
    var verb;
    if (aSel && bSel) verb = (cls==='hard' ? 'CONFLITO direto' : 'alerta entre selecionadas');
    else verb = (cls==='hard' ? 'bloqueia' : 'alerta sobre');
    var other = aSel ? c.b : c.a, picked = aSel ? c.a : c.b;
    var headline = (aSel && bSel)
        ? esc(OPT[c.a].label)+' ✕ '+esc(OPT[c.b].label)
        : esc(OPT[picked].label)+' → '+verb+' → '+esc(OPT[other].label);
    lines.push('<div class="cline '+cls+'"><span class="badge '+cls+'">'+esc(c.degree)+'</span> '+
               '<span class="ctype">'+esc(c.type||'')+'</span> — '+headline+
               '<small>'+esc(c.note||'')+'</small></div>');
  });
  box.innerHTML = lines.length ? lines.join('') :
    '<div class="empty">Nenhuma restrição disparada por esta seleção.</div>';
}

function renderSpace(){
  var n = countViable(selected);
  var picked = Object.keys(selected).length;
  document.getElementById('space').innerHTML =
    'Configurações viáveis compatíveis com a seleção ('+picked+'/'+DATA.params.length+' linhas): <b>'+
    n.toLocaleString('pt-BR')+'</b>';
}

function esc(s){ return String(s).replace(/[&<>"]/g, function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }

document.querySelectorAll('.opt').forEach(function(el){
  el.addEventListener('click', function(){
    var id = el.dataset.opt, p = el.dataset.param;
    if (el.classList.contains('blocked')){
      el.classList.add('flash');
      setTimeout(function(){ el.classList.remove('flash'); }, 500);
      return;
    }
    if (selected[p]===id) delete selected[p];   // clicar de novo deseleciona
    else selected[p] = id;
    recompute();
  });
});
document.getElementById('clear').addEventListener('click', function(){
  Object.keys(selected).forEach(function(k){ delete selected[k]; });
  recompute();
});
recompute();
</script>
</body></html>"""


def render_case_html(case: dict, cca: dict, generated: str) -> str:
    # Linhas no padrão GMA: cada parâmetro é uma linha; opções são as células.
    rows = []
    for idx, p in enumerate(case["parameters"]):
        cells = []
        for o in p["options"]:
            prov = o.get("proposed_by", "?")
            model = o.get("model")
            prov_txt = f"{prov}" + (f" · {model}" if model else "")
            cells.append(
                f'<div class="opt" data-param="{e(p["id"])}" data-opt="{e(o["id"])}">'
                f'<span class="ol">{e(o.get("label", o["id"]))}</span>'
                f'<span class="op">{e(prov_txt)}</span></div>'
            )
        desc = p.get("description", "")
        rows.append(
            f'<div class="row" style="--i:{idx}">'
            f'<div class="row-label"><span class="rl-no"></span>'
            f'<span class="rl-name">{e(p["label"])}</span>'
            + (f'<span class="rl-desc">{e(desc)}</span>' if desc else "")
            + "</div>"
            f'<div class="row-cells">{"".join(cells)}</div></div>'
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

    criteria_html = []
    for cr in case.get("criteria", []):
        kind = cr.get("kind", "")
        extra = cr.get("unit") or cr.get("scale") or ""
        meta = " · ".join(x for x in [kind, cr.get("direction", ""), extra] if x)
        criteria_html.append(
            f'<li><b>{e(cr.get("label", cr.get("id","")))}</b> '
            f'<span class="ctype">{e(meta)}</span>'
            + (f'<br><small>{e(cr.get("note",""))}</small>' if cr.get("note") else "")
            + "</li>"
        )

    a = case.get("assumptions", {})
    assumptions_parts = []
    if a.get("tariff_brl_per_kwh") is not None:
        assumptions_parts.append(f'tarifa R$ {a["tariff_brl_per_kwh"]}/kWh')
    if a.get("hours_per_month") is not None:
        assumptions_parts.append(f'{a["hours_per_month"]} h/mês')
    if a.get("pue") is not None:
        assumptions_parts.append(f'PUE {a["pue"]}')
    assumptions_txt = e(" · ".join(assumptions_parts)) or "—"

    q = cca["quotient"]
    q_txt = f"{q*100:.1f}%" if q is not None else "—"
    viable_txt = f'{cca["viable_configs"]:,}' if cca["enumerated"] else "—"

    # --- Camada de discussão (IBIS) + argumentação (Dung) ---
    args = case.get("arguments", []) or []
    grounded = grounded_extension(args)
    arg_by_id = {a["id"]: a for a in args if a.get("id")}
    param_of_opt = {}
    for p in case["parameters"]:
        for o in p["options"]:
            param_of_opt[o["id"]] = p
    ST = {"in": ("aceito", "ok"), "out": ("derrotado", "hard"), "undecided": ("indeciso", "weak")}

    def arg_html(a: dict) -> str:
        sttxt, stcls = ST[grounded.get(a.get("id", ""), "undecided")]
        stance = a.get("stance", "")
        stance_txt = {"pro": "pró", "con": "contra"}.get(stance, stance)
        by = a.get("by", "?")
        prov = e(by) + (f" · {e(a['model'])}" if a.get("model") else "")
        refuta = ""
        atks = a.get("attacks") or []
        if atks:
            ref = "; ".join(
                e((arg_by_id[x].get("claim", x)[:48] + "…")) if x in arg_by_id else e(x)
                for x in atks
            )
            refuta = f'<div class="arg-ref">refuta: {ref}</div>'
        return (
            f'<div class="arg {stcls}"><span class="badge {stcls}">{e(sttxt)}</span> '
            f'<span class="stance">{e(stance_txt)}</span> · <b>{e(label_for(case, a.get("target","")))}</b>'
            f'<div class="claim">{e(a.get("claim",""))}</div>{refuta}'
            f'<div class="arg-by">{prov}</div></div>'
        )

    ibis_html = ""
    if args:
        groups: dict = {}
        for a in args:
            p = param_of_opt.get(a.get("target"))
            key = p["id"] if p else "_outros"
            lbl = p["label"] if p else "Outros"
            groups.setdefault(key, {"label": lbl, "items": []})["items"].append(a)
        blocks = []
        for g in groups.values():
            blocks.append(
                f'<div class="issue"><div class="issue-q">{e(g["label"])}</div>'
                + "".join(arg_html(a) for a in g["items"])
                + "</div>"
            )
        ibis_html = "".join(blocks)
    n_in = sum(1 for v in grounded.values() if v == "in")
    n_out = sum(1 for v in grounded.values() if v == "out")
    ibis_summary = (
        f"{len(args)} argumentos · <b style='color:var(--ok)'>{n_in} aceitos</b> · "
        f"<b style='color:var(--signal)'>{n_out} derrotados</b> (semântica grounded de Dung)"
        if args
        else "Nenhum argumento registrado ainda."
    )

    # --- Matriz QOC (opções × critérios qualitativos) ---
    qual_crit = [c for c in case.get("criteria", []) if c.get("kind") == "qualitative"]
    qoc_html = ""
    if qual_crit:
        tables = []
        head = "".join(f"<th>{e(c.get('label', c['id']))}</th>" for c in qual_crit)
        for p in case["parameters"]:
            rows_q = []
            for o in p["options"]:
                sc = o.get("scores", {}) or {}
                cells = "".join(
                    (f"<td class='sc'>{sc[c['id']]}</td>" if c["id"] in sc else "<td class='sc na'>·</td>")
                    for c in qual_crit
                )
                rows_q.append(f"<tr><td class='opt-name'>{e(o.get('label', o['id']))}</td>{cells}</tr>")
            tables.append(
                f'<div class="qoc-block"><div class="qoc-p">{e(p["label"])}</div>'
                f'<table class="qoc"><thead><tr><th></th>{head}</tr></thead>'
                f'<tbody>{"".join(rows_q)}</tbody></table></div>'
            )
        qoc_html = "".join(tables)

    # Dados embutidos para a interatividade (sem depender de fetch; roda em file://).
    data = {
        "params": [
            {
                "id": p["id"],
                "label": p["label"],
                "options": [
                    {
                        "id": o["id"],
                        "label": o.get("label", o["id"]),
                        "rationale": o.get("rationale", ""),
                        "by": o.get("proposed_by", ""),
                        "model": o.get("model", ""),
                        "estimates": o.get("estimates", {}) or {},
                        "scores": o.get("scores", {}) or {},
                    }
                    for o in p["options"]
                ],
            }
            for p in case["parameters"]
        ],
        "constraints": [
            {
                "a": c["a"],
                "b": c["b"],
                "degree": c.get("degree", ""),
                "type": c.get("type", ""),
                "note": c.get("note", ""),
                "by": c.get("by", ""),
                "model": c.get("model", ""),
            }
            for c in case["constraints"]
        ],
        "criteria": case.get("criteria", []),
        "assumptions": case.get("assumptions", {}),
    }
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    return (
        CASE_TEMPLATE.replace("__CASE_ID__", e(case["id"]))
        .replace("__GENERATED__", e(generated))
        .replace("__N_PARAMS__", str(cca["n_parameters"]))
        .replace("__TOTAL__", f'{cca["total_configs"]:,}')
        .replace("__N_HARD__", str(cca["n_hard_constraints"]))
        .replace("__VIABLE__", viable_txt)
        .replace("__QUOTIENT__", q_txt)
        .replace("__ROWS__", "".join(rows))
        .replace(
            "__CONS__",
            "".join(constraints_html) or "<li>Nenhuma restrição ainda.</li>",
        )
        .replace(
            "__CRITERIA__",
            "".join(criteria_html) or "<li>Nenhum critério definido ainda.</li>",
        )
        .replace("__ASSUMPTIONS__", assumptions_txt)
        .replace("__IBIS_SUMMARY__", ibis_summary)
        .replace("__IBIS__", ibis_html or "<p class='note'>Sem argumentos ainda — proponha um pró/contra.</p>")
        .replace("__QOCMATRIX__", qoc_html or "<p class='note'>Sem critérios qualitativos ainda.</p>")
        .replace("__DATA_JSON__", data_json)
    )


def render_index(cases: list[dict]) -> str:
    items = "".join(
        f'<li><a href="{e(c["id"])}/index.html">{e(c["id"])}</a></li>' for c in cases
    )
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>idea-waddle</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root{{ --paper:#ece4d3; --panel:#f2ecdf; --ink:#1b1812; --ink-2:#544d3f; --rule:rgba(27,24,18,.16); --rule-2:rgba(27,24,18,.45); --signal:#bf3a1d; --blue:#234a63; }}
  *{{ box-sizing:border-box; }}
  body{{ margin:0; color:var(--ink); font-family:'IBM Plex Mono',ui-monospace,monospace; background-color:var(--paper);
    background-image:linear-gradient(var(--rule) 1px,transparent 1px),linear-gradient(90deg,var(--rule) 1px,transparent 1px); background-size:30px 30px; }}
  .topbar{{ position:fixed; top:0; left:0; right:0; height:5px; background:var(--signal); }}
  .wrap{{ max-width:760px; margin:0 auto; padding:64px 28px; }}
  h1{{ font-family:'Fraunces',serif; font-weight:600; font-size:clamp(48px,12vw,92px); letter-spacing:-.025em; margin:0 0 8px; line-height:.9; }}
  h1 .dot{{ color:var(--signal); }}
  .lead{{ font-family:'Fraunces',serif; font-style:italic; color:var(--ink-2); font-size:18px; max-width:52ch; margin:0; }}
  h2{{ font-family:'Fraunces',serif; font-weight:600; font-size:20px; margin:40px 0 12px; }}
  ul{{ list-style:none; padding:0; margin:0; border:1px solid var(--rule-2); background:var(--panel); }}
  li{{ border-top:1px solid var(--rule); }}
  li:first-child{{ border-top:0; }}
  li a{{ display:block; padding:15px 18px; color:var(--ink); text-decoration:none; }}
  li a:hover{{ background:var(--ink); color:var(--paper); }}
  a{{ color:var(--blue); }}
</style></head>
<body><div class="topbar"></div><div class="wrap">
<h1>idea<span class="dot">·</span>waddle</h1>
<p class="lead">Plataforma de colaboração criativa entre humanos e agentes de IA, usando o Git como espinha dorsal.</p>
<h2>Casos</h2><ul>{items}</ul>
</div></body></html>"""


def main() -> int:
    SITE_DIR.mkdir(exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # IW_CASE: um único diretório de caso (morphology/ na raiz dele) — usado por
    # um repositório de caso externo. Sem ele, varre CASES_DIR (multi-caso).
    single = os.environ.get("IW_CASE")
    if single:
        cases = [Path(single)]
    elif CASES_DIR.exists():
        cases = [
            d for d in sorted(CASES_DIR.iterdir())
            if (d / "morphology" / "params").is_dir()
        ]
    else:
        cases = []

    if not cases:
        print("Nenhum caso com morphology/params encontrado.")
        return 1

    case_id_override = os.environ.get("IW_CASE_ID")
    loaded = []
    for case_dir in cases:
        case = load_case(case_dir)
        if single and case_id_override:
            case["id"] = case_id_override
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
