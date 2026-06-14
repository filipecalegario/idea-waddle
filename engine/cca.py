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

    return {
        "id": case_dir.name,
        "parameters": params,
        "constraints": constraints,
        "criteria": criteria,
        "assumptions": assumptions,
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
<style>
  :root { --bg:#0f1117; --card:#1a1d27; --line:#2a2e3c; --txt:#e6e8ee; --mut:#9aa0b0;
          --acc:#7aa2f7; --hard:#f7768e; --weak:#e0af68; --ok:#9ece6a; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--txt); font:15px/1.5 system-ui,sans-serif; }
  .wrap { max-width:1180px; margin:0 auto; padding:24px; }
  h1 { font-size:24px; margin:0 0 4px; }
  .sub { color:var(--mut); margin-bottom:20px; }
  .stats { display:flex; flex-wrap:wrap; gap:12px; margin:16px 0 22px; }
  .stat { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:12px 16px; min-width:128px; }
  .stat b { display:block; font-size:22px; color:var(--acc); }
  .stat span { color:var(--mut); font-size:12px; }
  h2 { font-size:16px; margin:26px 0 10px; border-bottom:1px solid var(--line); padding-bottom:6px; }
  .hint { color:var(--mut); font-size:13px; margin:-4px 0 12px; }

  /* Caixa morfológica no padrão GMA: cada LINHA é um parâmetro; células = opções. */
  .gma { border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  .row { display:flex; align-items:stretch; border-bottom:1px solid var(--line); }
  .row:last-child { border-bottom:0; }
  .row-label { flex:0 0 175px; background:#222633; padding:12px; font-weight:600; font-size:13px;
               display:flex; align-items:center; border-right:1px solid var(--line); }
  .row-cells { flex:1; display:flex; flex-wrap:wrap; gap:8px; padding:10px; }
  .opt { flex:1 1 150px; min-width:140px; background:#12151d; border:1px solid var(--line);
         border-radius:8px; padding:8px 10px; cursor:pointer; transition:.12s; user-select:none; }
  .opt:hover { border-color:var(--acc); }
  .opt-label { display:block; font-size:13px; }
  .prov { display:block; color:var(--mut); font-size:11px; margin-top:3px; }
  .opt.selected { border-color:var(--acc); background:rgba(122,162,247,.16); box-shadow:0 0 0 1px var(--acc) inset; }
  .opt.blocked { opacity:.45; border-color:var(--hard); border-style:dashed; cursor:not-allowed; }
  .opt.blocked .opt-label { text-decoration:line-through; }
  .opt.warn { border-color:var(--weak); }
  .opt.flash { animation:flash .5s; }
  @keyframes flash { 0%,100%{background:#12151d;} 30%{background:rgba(247,118,142,.30);} }

  .panels { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:14px; }
  @media (max-width:760px){ .panels{ grid-template-columns:1fr; } .row{ flex-direction:column; } .row-label{ flex-basis:auto; border-right:0; border-bottom:1px solid var(--line);} }
  .panel { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px; }
  .panel h3 { margin:0 0 10px; font-size:14px; }
  .panel .empty { color:var(--mut); font-size:13px; }
  .selitem { border-left:3px solid var(--acc); padding:4px 0 4px 10px; margin-bottom:10px; }
  .selitem .p { color:var(--mut); font-size:11px; text-transform:uppercase; letter-spacing:.04em; }
  .selitem .l { font-size:14px; }
  .selitem .r { color:var(--mut); font-size:12px; margin-top:2px; }
  .selitem .by { color:var(--mut); font-size:11px; margin-top:3px; font-style:italic; }
  .cline { border-left:3px solid var(--line); padding:6px 0 6px 10px; margin-bottom:9px; font-size:13px; }
  .cline.hard { border-left-color:var(--hard); }
  .cline.weak { border-left-color:var(--weak); }
  .cline small { color:var(--mut); display:block; margin-top:2px; }
  .badge { font-size:11px; padding:1px 7px; border-radius:20px; }
  .badge.hard { background:rgba(247,118,142,.18); color:var(--hard); }
  .badge.weak { background:rgba(224,175,104,.18); color:var(--weak); }
  .space { margin-top:10px; font-size:13px; }
  .space b { color:var(--ok); }
  .estpanel { margin-top:14px; }
  .est-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; }
  .est { background:#12151d; border:1px solid var(--line); border-radius:8px; padding:10px 12px; }
  .est .k { color:var(--mut); font-size:12px; }
  .est .v { font-size:19px; color:var(--acc); margin-top:2px; }
  .est.qual .v { color:var(--ok); }
  .est .miss { color:var(--mut); font-size:13px; }
  .est .bar { height:6px; border-radius:4px; background:var(--line); margin-top:6px; overflow:hidden; }
  .est .bar > i { display:block; height:100%; background:var(--ok); }
  .est small { color:var(--mut); display:block; margin-top:3px; }
  .btn { background:#222633; color:var(--txt); border:1px solid var(--line); border-radius:7px;
         padding:6px 12px; cursor:pointer; font-size:13px; }
  .btn:hover { border-color:var(--acc); }
  ul.cons { list-style:none; padding:0; }
  ul.cons li { background:var(--card); border:1px solid var(--line); border-left:3px solid var(--line); border-radius:8px; padding:9px 12px; margin-bottom:8px; }
  ul.cons li.hard { border-left-color:var(--hard); }
  ul.cons li.weak { border-left-color:var(--weak); }
  .ctype { color:var(--mut); font-size:12px; }
  .cons small { color:var(--mut); }
  footer { color:var(--mut); font-size:12px; margin-top:32px; border-top:1px solid var(--line); padding-top:12px; }
  a { color:var(--acc); }
</style></head>
<body><div class="wrap">
  <h1>Caixa morfológica viva — __CASE_ID__</h1>
  <div class="sub">Plataforma <b>idea-waddle</b> · colaboração criativa humano + agente sobre Git ·
    gerado em __GENERATED__</div>

  <div class="stats">
    <div class="stat"><b>__N_PARAMS__</b><span>parâmetros</span></div>
    <div class="stat"><b>__TOTAL__</b><span>configurações totais</span></div>
    <div class="stat"><b>__N_HARD__</b><span>restrições (poda)</span></div>
    <div class="stat"><b>__VIABLE__</b><span>configurações viáveis</span></div>
    <div class="stat"><b>__QUOTIENT__</b><span>espaço de solução</span></div>
  </div>

  <h2>Explorar a caixa morfológica</h2>
  <div class="hint">Clique numa célula por linha para montar uma configuração. As opções
    <b style="color:var(--hard)">incompatíveis</b> com a sua seleção ficam bloqueadas; as
    <b style="color:var(--weak)">fracas</b> (alerta) seguem selecionáveis. Cada seleção mostra o comentário da célula e os caminhos de restrição ativados.</div>
  <div class="gma" id="gma">__ROWS__</div>

  <div class="panels">
    <div class="panel">
      <h3>Seleção atual <button class="btn" id="clear" style="float:right">Limpar</button></h3>
      <div id="selection"><div class="empty">Nenhuma célula selecionada.</div></div>
      <div class="space" id="space"></div>
    </div>
    <div class="panel">
      <h3>Caminhos de restrição ativos</h3>
      <div id="restrictions"><div class="empty">Selecione células para ver as restrições disparadas.</div></div>
    </div>
  </div>

  <div class="panel estpanel">
    <h3>Estimativas da configuração (QOC)</h3>
    <div class="hint" style="margin:0 0 10px">Números são <b>placeholders a refinar</b> (premissas editáveis em
      <code>assumptions.yaml</code>; valores por opção em <code>params/*.yaml</code>). Tratar como ordem de grandeza.</div>
    <div id="estimates"><div class="empty">Selecione opções para estimar custo, potência e energia.</div></div>
  </div>

  <h2>Critérios de avaliação (QOC)</h2>
  <ul class="cons">__CRITERIA__</ul>
  <div class="hint">Premissas (placeholders, editáveis em <code>assumptions.yaml</code>): __ASSUMPTIONS__</div>

  <h2>Todas as restrições (referência)</h2>
  <ul class="cons">__CONS__</ul>

  <footer>
    Proveniência registrada por opção/restrição (quem · qual modelo). Diversidade é princípio do projeto —
    veja o <code>README.md</code>, o <code>AGENTS.md</code> e <code>docs/discovery/</code>.
    Restrições <span class="badge weak">weak</span> alertam mas não podam.
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
function quantCard(k, v, miss){
  var inner = (v!=null) ? '<div class="v">'+v+'</div>' : '<div class="miss">'+ (miss||'—') +'</div>';
  return '<div class="est"><div class="k">'+esc(k)+'</div>'+inner+'</div>';
}
function qualCard(k, v){
  if (v==null) return '<div class="est qual"><div class="k">'+esc(k)+'</div><div class="miss">—</div></div>';
  var pct = Math.max(0, Math.min(100, (v/5)*100));
  return '<div class="est qual"><div class="k">'+esc(k)+'</div>'+
         '<div class="v">'+ (Math.round(v*10)/10) +' <small style="display:inline">/5</small></div>'+
         '<div class="bar"><i style="width:'+pct+'%"></i></div></div>';
}
function renderEstimates(){
  var box = document.getElementById('estimates');
  if (!Object.keys(selected).length){
    box.innerHTML = '<div class="empty">Selecione opções para estimar custo, potência e energia.</div>'; return;
  }
  var E = computeEstimates(), cards = [];
  cards.push(quantCard('Total de GPUs', E.gpus!=null ? E.gpus.toLocaleString('pt-BR') : null, 'selecione a escala'));
  cards.push(quantCard('Custo de capital', E.capex!=null ? fmtBRL(E.capex) : null, 'selecione hardware + escala'));
  cards.push(quantCard('Potência', E.powerKw!=null ? (Math.round(E.powerKw*10)/10)+' kW' : null, 'selecione hardware + escala'));
  cards.push(quantCard('Energia', E.energy!=null ? (fmtBRL(E.energy)+'/mês') : null, 'depende da potência'));
  DATA.criteria.filter(function(c){ return c.kind==='qualitative'; }).forEach(function(c){
    cards.push(qualCard(c.label, aggScore(c.id, E.scoreAgg[c.id])));
  });
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
    for p in case["parameters"]:
        cells = []
        for o in p["options"]:
            prov = o.get("proposed_by", "?")
            model = o.get("model")
            prov_txt = f"{prov}" + (f" · {model}" if model else "")
            cells.append(
                f'<div class="opt" data-param="{e(p["id"])}" data-opt="{e(o["id"])}">'
                f'<span class="opt-label">{e(o.get("label", o["id"]))}</span>'
                f'<span class="prov">{e(prov_txt)}</span></div>'
            )
        rows.append(
            f'<div class="row"><div class="row-label">{e(p["label"])}</div>'
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
