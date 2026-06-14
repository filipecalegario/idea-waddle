# Discovery 03 — Caixa morfológica da plataforma (inception)

> **Status:** artefato de decisão (Discovery)
> **Data:** 2026-06-14
> **O que é isto:** você pediu, em tom de *inception*, uma caixa morfológica para decidir **como construir a própria plataforma de colaboração criativa**. Aqui estão os parâmetros de design, as opções por parâmetro e algumas restrições de consistência (CCA). A recomendação inicial está marcada com ⭐.

Cada **parâmetro** é uma dimensão de decisão; cada **opção** é um valor possível. Uma "configuração" da plataforma = escolher uma opção por parâmetro, respeitando as restrições no fim.

---

## Parâmetros × Opções

### P1 — Substrato de versionamento
| Opção | Notas |
|---|---|
| ⭐ **GitHub** | maior alcance ("já vem do GitHub", como você prefere); Actions, Pages, fork/PR nativos; onde humanos e agentes já estão |
| GitLab (self-hosted) | soberania de dados (relevante p/ UFPE); CI nativo; menor alcance público |
| Git puro + forja alternativa (Gitea/Forgejo) | controle total, baixo alcance |
| Radicle (Git P2P) | descentralizado de verdade; ecossistema imaturo, pouca gente |

### P2 — Unidade de contribuição
| Opção | Notas |
|---|---|
| ⭐ **PR de arquivo Markdown estruturado** (front-matter YAML) | rastreável, versionável, parseável por agente; casa com `001-`, `002-` |
| Issues + labels | baixa fricção p/ humanos; menos estruturado; difícil versionar estado |
| GitHub Discussions | bom p/ conversa aberta; fora do versionamento Git |
| Formulário → bot abre PR | menor fricção p/ leigos; exige tooling extra |

### P3 — Artefato de síntese central
| Opção | Notas |
|---|---|
| ⭐ **Caixa morfológica + CCA** | seu pedido explícito; ótimo p/ opções + restrições; gera "caminhos de decisão" |
| Grafo IBIS (Questões/Posições/Argumentos) | melhor p/ *discussão*; complementar, não concorrente |
| QOC (Questions-Options-Criteria) | ponte natural entre IBIS e a caixa; adiciona critérios de avaliação |
| Argumentation Framework (Dung) | poda automática de argumentos; mais técnico/abstrato |
| **Combinação em camadas** (IBIS→QOC→Caixa+CCA→AAF) | mais rico; mais complexo de implementar (ver Discovery 02) |

### P4 — Motor de consolidação (quem lê PRs e atualiza o estado)
| Opção | Notas |
|---|---|
| Agente único | simples; risco de **um só modelo dominar** (anti-diversidade) |
| ⭐ **Swarm multi-modelo** (modelos diferentes, papéis diferentes) | encarna o princípio de diversidade; mais caro/complexo |
| Humano curador + agente assistente | máximo controle; não escala |
| Híbrido: swarm propõe, humano ratifica | equilíbrio recomendado p/ governança |

### P5 — Site vivo (publicação do estado consolidado)
| Opção | Notas |
|---|---|
| ⭐ **GitHub Pages + Actions** (gera a cada PR/merge) | zero infra extra; deploy preview por PR = "como ficaria se aceito" |
| Netlify/Vercel | previews ricos; dependência externa |
| App dedicado (ex.: Next.js + backend) | interatividade máxima; mais custo/manutenção |
| Static site generator (Docusaurus/Astro/MkDocs) | bom meio-termo; combina com Pages |

### P6 — Protocolo de contexto para agentes
| Opção | Notas |
|---|---|
| ⭐ **AGENTS.md** | padrão emergente (AAIF/Linux Foundation); qualquer agente lê |
| MCP server dedicado | acesso uniforme a repo/ferramentas; mais setup |
| Ambos (AGENTS.md + MCP) | contexto + acesso; recomendado quando amadurecer |
| Convenção própria (custom) | flexível; não interoperável |

### P7 — Modelo de governança / merge
| Opção | Notas |
|---|---|
| ⭐ **Human-in-the-loop** (PR só mergeia com aprovação humana) | lição dos incidentes "AI maintainer"; seguro |
| Final Comment Period estilo Rust | bom p/ deliberação madura; mais lento |
| Auto-merge com veto humano | rápido; arriscado no início |
| Quorum multi-agente + ratificação humana | encarna diversidade + segurança |

### P8 — Política de diversidade (anti-dominância de um modelo)
| Opção | Notas |
|---|---|
| ⭐ **Quorum de modelos distintos** (ex.: ≥2 famílias concordam) | reduz viés de um único LLM |
| Rodízio de modelos por ciclo | diversidade temporal; mais simples |
| Etiquetagem de proveniência (quem/qual modelo disse o quê) | transparência mínima obrigatória |
| Cotas humano:agente por ciclo | garante voz humana; exige medição |

### P9 — Granularidade do ciclo / linha do tempo
| Opção | Notas |
|---|---|
| ⭐ **Arquivos numerados `NNN-slug.md` por ciclo** | seu padrão preferido; marcos discretos legíveis |
| Tags/milestones do Git | nativo; menos visível p/ leigos |
| Snapshots automáticos do estado da caixa | reprodutível; requer tooling |
| Combinação (arquivos `NNN-` + tags) | marcos + genealogia contínua (recomendado) |

---

## Restrições de consistência (CCA) — exemplos iniciais

| Par incompatível / acoplado | Tipo | Observação |
|---|---|---|
| `Radicle` (P1) × `GitHub Pages` (P5) | empírica | Pages é específico do GitHub; exigiria outro publicador |
| `Issues/Discussions` (P2) × `Caixa morfológica versionada` (P3) | empírica | conteúdo fora do Git dificulta versionar o estado da caixa |
| `Agente único` (P4) × `Quorum de modelos` (P8) | lógica | quorum exige ≥2 modelos |
| `Auto-merge` (P7) × princípio de diversidade/governança | normativa | contraria a lição "humano dispõe" no início |
| `GitLab self-hosted` (P1) × `maior alcance público` | normativa/empírica | soberania de dados ⟷ alcance: trade-off explícito a decidir |

---

## Configuração recomendada (caminho inicial sugerido)

> **GitHub** (P1) · **PR de Markdown estruturado** (P2) · **Caixa morfológica + CCA como núcleo, com IBIS/QOC como camada de discussão** (P3) · **Swarm multi-modelo que propõe + humano ratifica** (P4) · **GitHub Pages + Actions com SSG** (P5) · **AGENTS.md agora, MCP depois** (P6) · **Human-in-the-loop, evoluindo p/ FCP** (P7) · **Quorum de modelos + proveniência etiquetada** (P8) · **Arquivos `NNN-` + tags** (P9).

Esta é uma hipótese de partida — a graça do projeto é que **a própria plataforma pode ser usada para decidir a plataforma** (inception real). As decisões em aberto estão em `04-perguntas-provocacoes.md`.
