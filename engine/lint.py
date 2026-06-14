#!/usr/bin/env python3
"""
Linter do padrão de contribuição da plataforma idea-waddle.

Valida que parâmetros, opções, restrições, critérios e ciclos seguem o protocolo
descrito em AGENTS.md — incluindo a regra de **rastreabilidade** (agentes precisam
declarar o modelo) e as regras do CCA (restrição liga opções de parâmetros
diferentes; referências existem). Pensado para rodar na CI a cada PR.

Uso:
    pip install pyyaml
    python engine/lint.py            # valida todos os casos
    echo $?                          # 0 = ok, 1 = há erros

Variáveis de ambiente (opcionais):
    IW_CASES  diretório de casos (default: cases/)
    IW_CASE   um único diretório de caso (morphology/ na raiz); ignora IW_CASES

Saída: avisos (⚠, não bloqueiam) e erros (✗, bloqueiam / exit 1).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Falta a dependência PyYAML. Rode: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
# Origem dos casos é configurável (ver IW_CASES em engine/cca.py). Default: cases/.
CASES = Path(os.environ.get("IW_CASES", ROOT / "cases"))

DEGREES = {"incompatible", "weak", "ok"}
CTYPES = {"logical", "empirical", "normative"}
STATUS = {"proposed", "accepted", "superseded", "rejected"}
KINDS = {"quantitative", "qualitative"}
DIRECTIONS = {"minimize", "maximize"}
AGGS = {"sum", "min", "avg", "derived"}


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []
        self.warns: list[tuple[str, str]] = []

    def err(self, where: str, msg: str) -> None:
        self.errors.append((where, msg))

    def warn(self, where: str, msg: str) -> None:
        self.warns.append((where, msg))


def rel(p: Path) -> str:
    # Robusto a casos fora do ROOT (ex.: IW_CASES apontando p/ outro repo).
    for base in (ROOT, CASES, CASES.parent):
        try:
            return str(p.relative_to(base))
        except ValueError:
            continue
    return str(p)


def load_yaml(path: Path, rep: Report):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as ex:  # noqa: BLE001
        rep.err(rel(path), f"YAML inválido: {ex}")
        return None


def front_matter(path: Path, rep: Report):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except Exception as ex:  # noqa: BLE001
        rep.err(rel(path), f"front-matter YAML inválido: {ex}")
        return None


def is_agent(who) -> bool:
    return isinstance(who, str) and who.startswith("agent:")


def lint_case(case_dir: Path, rep: Report) -> None:
    # 1) critérios (carrega primeiro p/ checar coerência dos scores)
    crit_ids: set[str] = set()
    crfile = case_dir / "morphology" / "criteria.yaml"
    if crfile.exists():
        d = load_yaml(crfile, rep) or {}
        for cr in d.get("criteria", []) or []:
            cid = cr.get("id")
            if not cid:
                rep.err(rel(crfile), "critério sem id")
                continue
            crit_ids.add(cid)
            if cr.get("kind") not in KINDS:
                rep.err(rel(crfile), f"{cid}: kind inválido (use {sorted(KINDS)})")
            if cr.get("direction") not in DIRECTIONS:
                rep.err(rel(crfile), f"{cid}: direction inválido (use {sorted(DIRECTIONS)})")
            if cr.get("aggregation") not in AGGS:
                rep.err(rel(crfile), f"{cid}: aggregation inválido (use {sorted(AGGS)})")

    # 2) parâmetros e opções
    option_param: dict[str, str] = {}  # opt id -> param id
    params_dir = case_dir / "morphology" / "params"
    if not params_dir.is_dir():
        rep.err(rel(case_dir), "falta morphology/params/")
    else:
        for f in sorted(params_dir.glob("*.yaml")):
            data = load_yaml(f, rep)
            if data is None:
                continue
            p = data.get("parameter")
            if not isinstance(p, dict):
                rep.err(rel(f), "falta a chave de topo 'parameter'")
                continue
            if not p.get("id"):
                rep.err(rel(f), "parameter.id ausente")
            if not p.get("label"):
                rep.err(rel(f), "parameter.label ausente")
            pid = p.get("id")
            opts = p.get("options")
            if not isinstance(opts, list) or not opts:
                rep.err(rel(f), "parameter.options vazio ou ausente")
                continue
            for o in opts:
                if not isinstance(o, dict):
                    rep.err(rel(f), "opção não é um mapa")
                    continue
                oid = o.get("id")
                if not oid:
                    rep.err(rel(f), "opção sem id")
                    continue
                if oid in option_param:
                    rep.err(rel(f), f"id de opção duplicado: {oid}")
                option_param[oid] = pid
                if not str(oid).startswith("opt."):
                    rep.warn(rel(f), f"id '{oid}' não segue a convenção opt.<param>.<slug>")
                if not o.get("label"):
                    rep.err(rel(f), f"{oid}: label ausente")
                if not o.get("proposed_by"):
                    rep.err(rel(f), f"{oid}: proposed_by ausente (rastreabilidade)")
                elif is_agent(o.get("proposed_by")) and not o.get("model"):
                    rep.err(rel(f), f"{oid}: contribuição de agente sem 'model' (rastreabilidade)")
                st = o.get("status")
                if not st:
                    rep.warn(rel(f), f"{oid}: status ausente (use {sorted(STATUS)})")
                elif st not in STATUS:
                    rep.err(rel(f), f"{oid}: status inválido '{st}'")
                sc = o.get("scores") or {}
                if not isinstance(sc, dict):
                    rep.err(rel(f), f"{oid}: scores deve ser um mapa")
                else:
                    for k, v in sc.items():
                        if not isinstance(v, (int, float)) or isinstance(v, bool) or not (1 <= v <= 5):
                            rep.err(rel(f), f"{oid}: score '{k}'={v} fora do intervalo 1–5")
                        elif crit_ids and k not in crit_ids:
                            rep.warn(rel(f), f"{oid}: score '{k}' não corresponde a nenhum critério definido")
                est = o.get("estimates") or {}
                if not isinstance(est, dict):
                    rep.err(rel(f), f"{oid}: estimates deve ser um mapa")
                else:
                    for k, v in est.items():
                        if not isinstance(v, (int, float)) or isinstance(v, bool):
                            rep.err(rel(f), f"{oid}: estimate '{k}' não é numérico")

    # 3) restrições (CCA)
    cfile = case_dir / "morphology" / "constraints.yaml"
    if cfile.exists():
        d = load_yaml(cfile, rep) or {}
        seen: set = set()
        for c in d.get("constraints", []) or []:
            a, b = c.get("a"), c.get("b")
            for x in (a, b):
                if x not in option_param:
                    rep.err(rel(cfile), f"restrição referencia opção inexistente: {x}")
            if a in option_param and b in option_param and option_param[a] == option_param[b]:
                rep.err(rel(cfile), f"restrição entre opções do MESMO parâmetro: {a} × {b}")
            key = frozenset((a, b))
            if key in seen:
                rep.warn(rel(cfile), f"restrição duplicada: {a} × {b}")
            seen.add(key)
            if c.get("degree") not in DEGREES:
                rep.err(rel(cfile), f"{a}×{b}: degree inválido (use {sorted(DEGREES)})")
            if c.get("type") not in CTYPES:
                rep.err(rel(cfile), f"{a}×{b}: type inválido (use {sorted(CTYPES)})")
            if not c.get("by"):
                rep.err(rel(cfile), f"{a}×{b}: 'by' ausente (rastreabilidade)")
            elif is_agent(c.get("by")) and not c.get("model"):
                rep.err(rel(cfile), f"{a}×{b}: contribuição de agente sem 'model'")

    # 3b) argumentos (IBIS + Dung)
    argfile = case_dir / "morphology" / "arguments.yaml"
    if argfile.exists():
        d = load_yaml(argfile, rep) or {}
        arg_list = d.get("arguments", []) or []
        arg_ids = set()
        for a in arg_list:
            aid = a.get("id")
            if not aid:
                rep.err(rel(argfile), "argumento sem id")
                continue
            if aid in arg_ids:
                rep.err(rel(argfile), f"id de argumento duplicado: {aid}")
            arg_ids.add(aid)
            if a.get("stance") not in {"pro", "con"}:
                rep.err(rel(argfile), f"{aid}: stance inválido (use pro|con)")
            if not a.get("target"):
                rep.err(rel(argfile), f"{aid}: target ausente")
            elif a["target"] not in option_param:
                rep.warn(rel(argfile), f"{aid}: target '{a['target']}' não é uma opção conhecida")
            if not a.get("claim"):
                rep.err(rel(argfile), f"{aid}: claim ausente")
            if not a.get("by"):
                rep.err(rel(argfile), f"{aid}: 'by' ausente (rastreabilidade)")
            elif is_agent(a.get("by")) and not a.get("model"):
                rep.err(rel(argfile), f"{aid}: contribuição de agente sem 'model'")
        for a in arg_list:  # referências de ataque (depois de coletar todos os ids)
            for tgt in a.get("attacks", []) or []:
                if tgt not in arg_ids:
                    rep.err(rel(argfile), f"{a.get('id')}: ataca argumento inexistente '{tgt}'")

    # 4) ciclos (linha do tempo)
    cyc = case_dir / "cycles"
    if cyc.is_dir():
        for f in sorted(cyc.glob("*.md")):
            if not re.match(r"^\d{3}-", f.name):
                rep.warn(rel(f), "nome fora do padrão NNN-slug.md")
            fm = front_matter(f, rep)
            if fm is None:
                rep.err(rel(f), "sem front-matter YAML (--- ... ---)")
                continue
            for k in ("cycle", "slug", "status", "authored_by"):
                if k not in fm:
                    rep.warn(rel(f), f"front-matter sem '{k}'")
            if is_agent(fm.get("authored_by")) and not fm.get("model"):
                rep.err(rel(f), "authored_by é agente, mas falta 'model' (rastreabilidade)")


def main() -> int:
    rep = Report()
    single = os.environ.get("IW_CASE")
    if single:
        cases = [Path(single)]
    elif CASES.exists():
        cases = [d for d in sorted(CASES.iterdir()) if (d / "morphology").is_dir()]
    else:
        cases = []
    if not cases:
        print("Nenhum caso com morphology/ encontrado.")
        return 1

    for d in cases:
        lint_case(d, rep)

    for where, msg in rep.warns:
        print(f"⚠ {where}: {msg}")
    for where, msg in rep.errors:
        print(f"✗ {where}: {msg}")
    print()

    n_cases = len(cases)
    if rep.errors:
        print(f"FALHOU — {len(rep.errors)} erro(s), {len(rep.warns)} aviso(s) em {n_cases} caso(s).")
        return 1
    print(f"OK — padrão válido em {n_cases} caso(s). {len(rep.warns)} aviso(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
