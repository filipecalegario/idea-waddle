# Evolução do projeto — fio da meada

> **Registro vivo.** Este arquivo guarda a linha do tempo das decisões e do que foi construído, para não perdermos o contexto entre sessões. Atualize-o a cada marco (nova decisão, nova capacidade, mudança de rumo).
>
> Convenções: datas absolutas (AAAA-MM-DD). Cada decisão registra **o quê**, **por quê** e **consequência**. Itens em aberto ficam na seção [Decisões em aberto](#decisões-em-aberto).

## Visão em uma frase
Plataforma de **colaboração criativa entre humanos e agentes de IA usando o Git como espinha dorsal** — propor/forkar/mesclar *ideias* (não código) via PR, consolidadas por agentes numa **caixa morfológica viva** com restrições, linha do tempo e rastreabilidade total. **Primeiro caso de uso:** arquitetura do cluster de inferência do CIn-UFPE (não é o produto; é um caso).

---

## Linha do tempo

### 2026-06-14 — Gênese (INTENT.md)
- Origem: transcrição de áudio do idealizador (Filipe) em [`/INTENT.md`](../../INTENT.md).
- Necessidade central: uma chamada pública para especificar, de forma colaborativa (humanos + agentes), um cluster de **inferência** para o CIn-UFPE (complementando o cluster *batch* "Apuana"), chegando a **caminhos de decisão** com estimativas de custo/energia/aquisição de GPUs (mercado americano vs. chinês) para a diretoria do CIn.
- Pedidos explícitos: usar Git como espinha dorsal; `AGENTS.md` com contexto + protocolo; **caixa morfológica** com restrições; **site vivo** atualizado a cada contribuição; rastreabilidade; linha do tempo por ciclos (`001-`, `002-`); pesquisar prior art e fundamentos teóricos; ser provocado com perguntas.

### 2026-06-14 — Discovery (pesquisa + fundamentação)
- Pesquisa registrada em [`/docs/discovery/`](../discovery/) (com referências verificáveis):
  - **Prior art** ([`01`](../discovery/01-prior-art.md)): a ideia existe **fragmentada** em 4 tradições (governance-as-code, deliberação coletiva, agentes em repositórios, docs-as-code). **Conclusão: a lacuna é real** — ninguém reúne versionamento + síntese por IA + deliberação + site vivo + diversidade rastreável. Referenciais a estudar/forkar: Log4brains, Talk to the City, GitHub Agentic Workflows; caso vTaiwan.
  - **Fundamentos teóricos** ([`02`](../discovery/02-fundamentos-teoricos.md)): caixa morfológica de Zwicky + **Cross-Consistency Assessment (CCA)** para restrições; IBIS/Dialogue Mapping e QOC para a discussão; argumentação de Dung/AIF para poda automática; memética + Git para genealogia de ideias. Em 3 camadas: discussão → solução → raciocínio automático.
  - **Caixa morfológica da plataforma** ([`03`](../discovery/03-caixa-morfologica-da-plataforma.md)): o "inception" — 9 parâmetros de design da própria plataforma com opções e restrições.
  - **Provocações** ([`04`](../discovery/04-perguntas-provocacoes.md)): 22 perguntas em aberto.

### 2026-06-14 — Princípio incorporado: diversidade
- **Decisão:** a justificativa central do projeto é a **diversidade** — de visões humanas e de **modelos de IA**, evitando que um único LLM domine a discussão. Rastreabilidade (Git) é a base da confiança.
- **Por quê:** uma pessoa/um modelo só não enxerga tudo; pluralidade reduz pontos cegos e viés (inclusive geopolítico, relevante num projeto que decide comprar GPUs do mercado americano vs. chinês).
- **Consequência:** registrado no [`/README.md`](../../README.md); virou princípio não-negociável no [`/AGENTS.md`](../../AGENTS.md) (proveniência por modelo, quorum/segunda opinião antes de consolidar).

### 2026-06-14 — Decisão: a plataforma é genérica; CIn é o 1º caso
- **Decisão:** idea-waddle é uma plataforma genérica de colaboração criativa; o cluster do CIn é o **Caso 0**.
- **Consequência:** estrutura `cases/<caso>/` separando o motor genérico dos conteúdos específicos.

### 2026-06-14 — Decisões de rumo (via consulta ao usuário)
- **Próximo passo = Protótipo mínimo vivo.** Construir o caso do CIn com caixa morfológica + CCA + site vivo, em vez de só refinar documentos.
- **Profundidade do artefato = "Caixa agora, camadas depois".** Implementar caixa morfológica + CCA primeiro, deixando **ganchos** (IDs estáveis, `ibis_issue`, proveniência por modelo, front-matter) para acoplar IBIS/QOC/Dung em fases seguintes.

### 2026-06-14 — Fundação construída (commit `e21681e`, push na main)
- [`/README.md`](../../README.md): visão + justificativa (diversidade) + CIn como 1º caso.
- [`/AGENTS.md`](../../AGENTS.md): contexto + protocolo de colaboração (human-in-the-loop; tipos de contribuição; padrão de escrita; como agentes processam).
- [`/cases/cin-ufpe-inference-cluster/`](../../cases/cin-ufpe-inference-cluster/): caixa morfológica inicial (6 parâmetros), restrições CCA e ciclo [`001-abertura.md`](../../cases/cin-ufpe-inference-cluster/cycles/001-abertura.md).
- [`/engine/cca.py`](../../engine/cca.py): motor que lê os YAML, roda o CCA e gera o site vivo. Resultado atual: **6 params · 1.296 configurações · 783 viáveis (60,4%) · 6 restrições**.
- [`/.github/workflows/build-site.yml`](../../.github/workflows/build-site.yml): CI regenera a cada PR e publica no GitHub Pages a cada push na main.

### 2026-06-14 — Site vivo ficou interativo (padrão GMA + exploração)
- **Decisão (pedido do usuário):** layout no **padrão original da GMA — por linha** (cada linha = um parâmetro/feature; células = opções) e **interatividade**.
- **O que foi feito:** clicar células para montar uma configuração; painel com o **comentário** de cada célula selecionada (rationale + proveniência); opções **incompatíveis** ficam bloqueadas e as **weak** em alerta; painel de **caminhos de restrição ativos**; contador dinâmico de configurações viáveis compatíveis com a seleção. Tudo dirigido pelos mesmos YAML; funciona em `file://` e na CI.

---

## Estado atual (snapshot)
- **Fase:** fim do Discovery / início do protótipo. Ciclo **001 (abertura)** aberto, em modo *divergir*.
- **Repositório:** `github.com/filipecalegario/idea-waddle`, branch `main`.
- **Camada ativa:** caixa morfológica + CCA + site vivo interativo. Camadas IBIS/QOC/Dung: ganchos prontos, ainda não implementadas.
- **Pendência operacional:** habilitar GitHub Pages (Settings → Pages → Source: GitHub Actions) para o site ir ao ar.

## Decisões em aberto
(ver detalhes em [`/docs/discovery/04-perguntas-provocacoes.md`](../discovery/04-perguntas-provocacoes.md))
- **Substrato:** GitHub (preferência atual) vs. GitLab self-hosted (soberania de dados p/ UFPE).
- **Política de diversidade operacional:** quorum de modelos? cotas humano:agente por ciclo? como medir diversidade?
- **Critérios de avaliação (QOC) e estimativas quantitativas** (custo de capital, kW, R$/mês, prazo, risco de fornecimento) por configuração.
- **Governança:** rate-limiting de agentes, identidade verificável, fronteira do que só humanos podem fazer.
- **Entregável final p/ a diretoria:** um caminho recomendado vs. N caminhos com trade-offs.
- **Build vs. fork** de Talk to the City / Log4brains.

## Próximos passos candidatos
1. Acoplar a **camada de critérios (QOC) + estimativas** de custo/energia por configuração.
2. Adicionar parâmetros faltantes ao Caso 0: **refrigeração/energia**, **armazenamento**, **financiamento**, **modelos de LLM a servir**, **políticas de uso/cota**.
3. Buscar **segunda opinião de outra família de modelos** sobre a caixa semeada (princípio de diversidade).
4. Implementar **lint de PR** (validação do padrão de escrita) e o loop *agente propõe → humano ratifica*.
5. Habilitar o GitHub Pages e divulgar a chamada pública.

---

## Como manter este registro
A cada marco relevante, adicione uma entrada datada na Linha do tempo (o quê / por quê / consequência), atualize o Snapshot e mova itens entre "em aberto" e "decidido". Os ciclos numerados em `cases/*/cycles/NNN-*.md` continuam sendo o registro fino por caso; este arquivo é a visão macro do projeto inteiro.
