# Discovery — Índice e sumário executivo

> **Fase:** Discovery · **Data:** 2026-06-14
> Esta pasta registra a pesquisa e os artefatos de decisão que fundamentam o projeto. Tudo fica versionado no repositório (não só em memória de um assistente), com as referências verificáveis.

## O que perguntamos
Como construir uma **plataforma de colaboração criativa entre humanos e agentes de IA, usando o Git como espinha dorsal** — onde se propõem, bifurcam e mesclam *ideias* (não código), consolidadas numa **caixa morfológica viva** com restrições, linha do tempo e total rastreabilidade de autoria. Primeiro caso de uso: a arquitetura do cluster de inferência do CIn-UFPE.

## O que descobrimos (resumo)
- **A ideia é viável e a lacuna é real.** As peças existem separadas — governance-as-code (RFC/ADR), deliberação coletiva (Pol.is, Talk to the City), agentes em repositórios (GitHub Agentic Workflows), docs-as-code (sites vivos) — mas **ninguém reuniu as cinco capacidades** (versionamento + síntese por IA + deliberação + site vivo + diversidade rastreável). Detalhes em [`01-prior-art.md`](01-prior-art.md).
- **Há método maduro para reusar.** A **caixa morfológica** (Zwicky) + **Cross-Consistency Assessment** (restrições entre opções) dão o esqueleto da solução; **IBIS/Dialogue Mapping** e **QOC** dão o esqueleto da discussão; **frameworks de argumentação (Dung)** permitem poda automática; **memética + Git** modelam a genealogia fork/merge de ideias. Detalhes em [`02-fundamentos-teoricos.md`](02-fundamentos-teoricos.md).
- **Padrões prontos para serializar no Git:** YAML (parâmetros/opções/restrições), AIF-JSON (grafo de argumentos), IBIS (vocabulário da discussão), AGENTS.md (contexto p/ agentes).
- **Governança não é opcional.** Incidentes reais de "AI maintainer" mostram que atribuição clara, rate-limiting e *human-in-the-loop* são obrigatórios.

## Artefatos desta fase
| Arquivo | Conteúdo |
|---|---|
| [`01-prior-art.md`](01-prior-art.md) | O que já existe; tabela de lacuna; referenciais a forkar (Log4brains, Talk to the City) |
| [`02-fundamentos-teoricos.md`](02-fundamentos-teoricos.md) | Caixa morfológica, CCA, IBIS, QOC, Toulmin, Delphi/NGT, Double Diamond, Dung/AIF, memética; com exemplos de modelagem em YAML/JSON |
| [`03-caixa-morfologica-da-plataforma.md`](03-caixa-morfologica-da-plataforma.md) | 9 parâmetros de design da plataforma × opções + restrições (CCA) + configuração recomendada (inception) |
| [`04-perguntas-provocacoes.md`](04-perguntas-provocacoes.md) | 22 perguntas em aberto para ampliar o espaço de ideias |

## Decisões em aberto (próximo passo)
Ver [`03`](03-caixa-morfologica-da-plataforma.md) (caminhos de plataforma) e [`04`](04-perguntas-provocacoes.md) (provocações). As mais pivotais: substrato (GitHub vs. GitLab self-hosted / soberania de dados), profundidade do artefato de síntese (só caixa morfológica vs. camadas IBIS→QOC→Caixa→AAF), e política de diversidade (quorum de modelos, proveniência, cotas humano:agente).
