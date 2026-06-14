# Evolução do projeto — fio da meada

> **Registro vivo.** Este arquivo guarda a linha do tempo das decisões e do que foi construído, para não perdermos o contexto entre sessões. Atualize-o a cada marco (nova decisão, nova capacidade, mudança de rumo).
>
> Convenções: datas absolutas (AAAA-MM-DD). Cada decisão registra **o quê**, **por quê** e **consequência**. Itens em aberto ficam na seção [Decisões em aberto](#decisões-em-aberto).

## Visão em uma frase
Plataforma de **colaboração criativa entre humanos e agentes de IA usando o Git como espinha dorsal** — propor/forkar/mesclar *ideias* (não código) via PR, consolidadas por agentes numa **caixa morfológica viva** com restrições, linha do tempo e rastreabilidade total. **Primeiro caso de uso:** arquitetura do cluster de inferência do CIn-UFPE (não é o produto; é um caso).

---

## Linha do tempo

### 2026-06-14 — Gênese
- Origem: transcrição de áudio do idealizador (Filipe), mantida em um **arquivo de origem privado**, fora do repositório público (não versionado, por privacidade).
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

### 2026-06-14 — Passo 1: camada QOC + estimativas de custo/energia
- **Decisão (consulta ao usuário):** estimativas **híbridas** (quantitativo para capex/potência/energia com premissas documentadas e editáveis + escores qualitativos 1-5 para critérios moles) e **placeholders plausíveis semeados** (marcados como "a refinar").
- **O que foi feito:**
  - [`morphology/criteria.yaml`](../../cases/cin-ufpe-inference-cluster/morphology/criteria.yaml): 6 critérios (capex, potência, energia/mês — derivados; soberania, risco de fornecimento, suporte — qualitativos com agregação `min`).
  - [`morphology/assumptions.yaml`](../../cases/cin-ufpe-inference-cluster/morphology/assumptions.yaml): premissas (tarifa R$/kWh, horas/mês, PUE) — placeholders.
  - `estimates`/`scores` adicionados às opções (`params/*.yaml`).
  - `engine/cca.py`: carrega critérios/premissas; o site agora exibe **Estimativas da configuração** (GPUs, capex, kW, R$/mês, escores com barra) recalculadas a cada seleção, + seção de Critérios (QOC) e premissas.
- **Validação:** H100 ×32 + Ethernet → capex ≈ R$9,02M · 33,6 kW · R$22.982/mês (ordens de grandeza coerentes).

### 2026-06-14 — Passo 2: parâmetros faltantes do Caso 0
- **O que foi feito:** adicionados 5 parâmetros à caixa do CIn — [`07-refrigeracao`](../../cases/cin-ufpe-inference-cluster/morphology/params/07-refrigeracao.yaml), [`08-armazenamento`](../../cases/cin-ufpe-inference-cluster/morphology/params/08-armazenamento.yaml), [`09-financiamento`](../../cases/cin-ufpe-inference-cluster/morphology/params/09-financiamento.yaml), [`10-modelos-llm`](../../cases/cin-ufpe-inference-cluster/morphology/params/10-modelos-llm.yaml), [`11-politicas-uso`](../../cases/cin-ufpe-inference-cluster/morphology/params/11-politicas-uso.yaml) — com estimates/scores placeholder e 3 novas restrições (refrigeração × escala/hardware).
- **Resultado:** **11 parâmetros · 419.904 configurações totais · 253.692 viáveis (60,4%)**. Refrigeração e armazenamento entram no capex; "Portfólio diverso" de modelos conecta ao princípio de diversidade.

### 2026-06-14 — Ajustes de UX e correção de restrições (feedback do usuário)
- **Quadro de estimativas movido para o topo** (logo após os indicadores, antes da caixa) e fixado (sticky): atualiza ao vivo conforme a seleção muda na caixa abaixo. Motivo: visibilidade imediata para quem usa.
- **Correção de consistência mercado × placas:** adicionadas restrições recíprocas — selecionar **mercado chinês** agora bloqueia H100/L40S/MI300 (sobra Ascend); **mercado americano** bloqueia Ascend. Espaço viável: 178.848 (42,6%) com 9 restrições.

### 2026-06-14 — Passo 3: segunda opinião (diversidade) — SIMULADA
- **Decisão (consulta ao usuário):** simular a 2ª opinião agora, com perspectiva deliberadamente diferente, registrada como contribuição rastreável `agent:revisor-2` (marcada como **simulação** de diversidade — não outra família real; substituir por revisão de família distinta quando possível).
- **O que foi feito:** ciclo [`002-segunda-opiniao.md`](../../cases/cin-ufpe-inference-cluster/cycles/002-segunda-opiniao.md) com crítica à semeadura (foco em capex, ausência de opex/sustentabilidade, lock-in, alternativas frugais). Contribuições reais à caixa por `agent:revisor-2`: nova opção *GPUs de consumo/refurbished*; novo critério *Sustentabilidade*; 2 restrições (consumo × mercado chinês / × escala média). Divergências Q-A..Q-F (provisão nuvem, federação c/ Apuana, contestar restrições, opex/prazo/carbono) deixadas como Questões para debate.
- **Resultado:** 11 params · **524.880 configurações · 233.280 viáveis (44,4%)** · 10 restrições. Proveniência distinta (`agent:discovery` vs `agent:revisor-2`) visível no site.

### 2026-06-14 — Redesign da interface (skill frontend-design)
- **Pedido do usuário:** sair do visual genérico de IA (dark-card/azul). Usada a skill **frontend-design**.
- **Direção estética:** *dossiê técnico / editorial científico* — fundo papel com grid milimetrado + grão sutil; tipografia com caráter (**Fraunces** display, **Archivo** corpo, **IBM Plex Mono** dados); réguas finas e sombras sólidas deslocadas; seções numeradas (§), marcas de registro nos cantos do instrumento; caixa morfológica como folha de especificação; estimativas como "leitura de instrumento" com medidores segmentados; células selecionáveis com estados estampados/hachurados; reveals escalonados no load (respeita prefers-reduced-motion). Tudo continua gerado por `engine/cca.py`.

### 2026-06-14 — Passo 4: lint de PR + loop "agente propõe → humano ratifica"
- **Lint:** [`engine/lint.py`](../../engine/lint.py) valida o padrão de contribuição (ids únicos/referências; CCA liga parâmetros diferentes; degree/type/status/kind válidos; **rastreabilidade** — agente sem `model` é erro; scores 1–5; front-matter de ciclos). Testado: passa no repo (0 erros) e pega 7/7 erros numa fixture quebrada.
- **CI:** novo job `lint` em [`build-site.yml`](../../.github/workflows/build-site.yml); `build` e `deploy` dependem dele — PR inválido falha e não é publicado.
- **Ratificação humana:** [`.github/CODEOWNERS`](../../.github/CODEOWNERS) (dono revisa) + [`pull_request_template.md`](../../.github/pull_request_template.md) com o protocolo. Nenhum PR é auto-mesclado.
- **Pendência operacional:** habilitar no GitHub a branch protection (require PR + review de Code Owners + status check `lint`).

### 2026-06-14 — Separação plataforma × caso, item 1: motor parametrizável
- **Contexto:** decidir separar o repo abstrato (plataforma idea-waddle: motor + protocolo) do concreto (caso do cluster CIn), mantendo o motor reusável. Plano em 5 passos (ver discussão); este é o **item 1**, reversível e sem mover arquivos.
- **O que foi feito:** `engine/cca.py` e `engine/lint.py` agora aceitam `IW_CASES` (origem dos casos) e `IW_SITE` (saída do site) por variável de ambiente; sem elas, o comportamento padrão (`cases/`, `site/`) é idêntico. `lint.rel()` ficou robusto a caminhos fora do repo.
- **Validação:** padrão inalterado; com `IW_CASES`/`IW_SITE` apontando p/ um diretório externo, motor e lint operam sobre o caso externo e geram o site lá, sem tocar no repo local. Abre caminho para o repo do caso CIn consumir o motor via checkout na CI (item 3).

### 2026-06-14 — Separação plataforma × caso, itens 2–3: caso CIn migrado para repo próprio
- **Item 2 (transferência com histórico):** `git subtree split --prefix=cases/cin-ufpe-inference-cluster` → branch `cin-split` (prefixo removido, 5 commits do caso preservados) → transferido para o novo repo `github.com/filipecalegario/cin-cluster-inferencia` (layout: `morphology/` e `cycles/` na raiz).
- **Item 3 (repo do caso autônomo):** lá foram criados README/AGENTS (fino, aponta p/ o protocolo canônico)/CALL + `.github/workflows/build-site.yml` que faz **checkout da idea-waddle** e roda o motor via `IW_CASE`, publicando o próprio Pages.
- **Suporte no motor:** `cca.py`/`lint.py` aceitam `IW_CASE` (um único diretório de caso, `morphology/` na raiz) e `IW_CASE_ID`; `load_case` resolve o id do nome do diretório. Validado contra o repo novo (id `cin-cluster-inferencia`, mesmos números).
- **Item 4:** resolvido a seguir (caso auto-referente).

### 2026-06-14 — Separação, item 4: caso auto-referente; CIn removido da plataforma
- **Decisão (usuário):** converter em caso auto-referente.
- **O que foi feito:** removido `cases/cin-ufpe-inference-cluster/` da idea-waddle; criado [`cases/idea-waddle-platform/`](../../cases/idea-waddle-platform/) — a caixa morfológica do **design da própria plataforma** (9 params, 4 restrições, critérios alcance/soberania/simplicidade), semeada a partir de `docs/discovery/03`. *Inception*: a plataforma demonstra o método com o próprio caso dela.
- **Resultado:** idea-waddle constrói `idea-waddle-platform` (9 params · 327.680 configs · 288.000 viáveis · 2 restrições hard). README/AGENTS atualizados: CIn aponta para o repo próprio; caso bundled é o auto-referente. Separação plataforma × caso **concluída**.

### 2026-06-14 — Passo 5: Pages no ar + chamada pública preparada
- **Privacidade:** `INTENT.md` (texto de origem do idealizador) removido do Git **inclusive do histórico** (`git filter-branch` + force-push); cópia local preservada (gitignored + backup fora do repo). Ref no spec corrigida.
- **idea-waddle tornada pública** (via API). **GitHub Pages habilitado** (source = Actions) nos dois repos; builds verdes (a CI do caso agora busca a plataforma pública). Sites no ar:
  - Plataforma: https://filipecalegario.github.io/idea-waddle/
  - Caso CIn (chamada viva): https://filipecalegario.github.io/cin-cluster-inferencia/
- **Kit de divulgação** no repo do caso: `.github/` com CODEOWNERS, pull_request_template e ISSUE_TEMPLATE (opção, restrição, parâmetro/critério, segunda opinião) + `ANNOUNCE.md` (textos curto/médio/e-mail + good first issues). O ato de divulgar (redes/e-mail) fica com o usuário.
- **Pendente do usuário:** branch protection das `main` (require PR + Code Owners + check `lint`); divulgar de fato.

### 2026-06-14 — Camadas IBIS + QOC (profunda) + Dung implementadas
- **IBIS (discussão):** `morphology/arguments.yaml` — cada parâmetro é uma Questão; opções são Posições; argumentos `pro`/`con` com `target` numa opção. Site mostra a seção "Discussão & argumentação" agrupada por Questão, com proveniência.
- **Dung (argumentação):** `attacks` entre argumentos formam um grafo; `grounded_extension()` no motor calcula quais argumentos sobrevivem (aceito/derrotado/indeciso). Demo: no caso da plataforma, o argumento "GitHub = lock-in/EUA" fica **derrotado** pelo de portabilidade.
- **QOC profunda:** `weight` nos critérios; site renderiza a **Matriz QOC** (opções × critérios) e um **Índice QOC ponderado** por configuração no painel de estimativas.
- **Motor/lint:** `cca.py` carrega `arguments.yaml`, computa grounded, renderiza as seções; `lint.py` valida argumentos (id único, stance pro/con, target/claim/by, ataques referenciam ids existentes, rastreabilidade). Dados de demo + pesos adicionados ao caso `idea-waddle-platform`. AGENTS.md documenta as quatro camadas. O caso CIn herda a capacidade via CI.

### 2026-06-14 — Visibilidade da evolução: mapa (Git) + ciclo de vida
- **Mapa de evolução:** o motor lê o histórico do Git (`git log`/`show`) e renderiza um **grafo com lanes** (bifurcações/merges) — cada nó é um commit (data · autor · porquê · chips de `+adicionado`/`−removido` de opções/argumentos), linkado ao commit no GitHub. Seção "Evolução & genealogia". Requer `fetch-depth: 0` na CI (ajustado nos dois repos).
- **Ciclo de vida (sem apagar):** opções com `status: superseded|rejected` + `reason` aparecem **riscadas com o motivo** e **saem do cálculo** (ex.: `opt.protocolo.custom` aposentada → total do caso da plataforma caiu de 327.680 p/ 245.760). lint avisa se aposentar sem `reason`.
- Mostra os três eixos pedidos: o que entrou/saiu (chips + status), por quê (mensagem/`reason`/`claim`), e a evolução no tempo (grafo). Bifurcações/merges aparecem conforme PRs reais são mesclados.

### 2026-06-14 — Estimativas genéricas (dirigidas por dados) — motor agnóstico
- **Problema (apontado pelo usuário):** o cálculo de estimativas estava acoplado ao cluster (`n_gpus`, `capex_per_gpu_brl`, PUE…) dentro do motor.
- **Solução:** o caso declara suas **métricas** (fórmulas) em `morphology/metrics.yaml`; o motor só soma os campos `estimates` das opções + `assumptions` e **avalia as expressões** (avaliador de expressão seguro em JS, sem `eval`). O modelo de custo do cluster saiu do motor e foi para o repo do CIn (`metrics.yaml`). O caso da plataforma não tem `metrics.yaml` → não exibe cards quantitativos (prova da genericidade). `lint` valida `metrics.yaml`. Corrigido também um NBSP residual no template.

## Estado atual (snapshot)
- **Fase:** chamada pública pronta para receber contribuições; **quatro camadas ativas** + motor agnóstico de domínio (Caixa/CCA · QOC · IBIS · Dung). Plataforma e caso CIn em **repositórios separados**, ambos com site vivo publicado.
- **Repositórios:** plataforma `github.com/filipecalegario/idea-waddle` (motor + protocolo + caso auto-referente); caso concreto `github.com/filipecalegario/cin-cluster-inferencia` (consome o motor via CI).
- **Caso bundled na plataforma:** `idea-waddle-platform` (auto-referente, 9 params). O caso do CIn (11 params, ciclos 001/002) vive no repo próprio.
- **Camada ativa:** caixa morfológica + CCA + **QOC (critérios + estimativas)** no site vivo interativo (tema dossiê). **Governança:** lint na CI + ratificação humana (CODEOWNERS). Camadas IBIS/Dung: ganchos prontos, ainda não implementadas.
- **Pendência operacional:** em **ambos** os repos, habilitar GitHub Pages (Settings → Pages → Source: GitHub Actions) e a branch protection da `main` (ver CODEOWNERS). No repo do caso, a CI faz checkout público da idea-waddle (se ela for privada, precisa de token).

## Decisões em aberto
(ver detalhes em [`/docs/discovery/04-perguntas-provocacoes.md`](../discovery/04-perguntas-provocacoes.md))
- **Substrato:** GitHub (preferência atual) vs. GitLab self-hosted (soberania de dados p/ UFPE).
- **Política de diversidade operacional:** quorum de modelos? cotas humano:agente por ciclo? como medir diversidade?
- **Refinar os placeholders** de estimativas/escores com números pesquisados/medidos (tarifa real de PE/UFPE, preços de GPU, PUE).
- **Governança:** rate-limiting de agentes, identidade verificável, fronteira do que só humanos podem fazer.
- **Entregável final p/ a diretoria:** um caminho recomendado vs. N caminhos com trade-offs.
- **Build vs. fork** de Talk to the City / Log4brains.

## Próximos passos candidatos
1. ✅ ~~Acoplar a **camada de critérios (QOC) + estimativas** de custo/energia por configuração.~~ (feito 2026-06-14)
2. ✅ ~~Adicionar parâmetros faltantes ao Caso 0: **refrigeração/energia**, **armazenamento**, **financiamento**, **modelos de LLM a servir**, **políticas de uso/cota**.~~ (feito 2026-06-14)
3. ✅ ~~Buscar **segunda opinião de outra família de modelos** sobre a caixa semeada (princípio de diversidade).~~ (feito 2026-06-14, SIMULADO — substituir por família real)
4. ✅ ~~Implementar **lint de PR** (validação do padrão de escrita) e o loop *agente propõe → humano ratifica*.~~ (feito 2026-06-14)
5. ✅ ~~Habilitar o GitHub Pages e divulgar a chamada pública.~~ (Pages no ar + kit de divulgação prontos em 2026-06-14; divulgação efetiva a cargo do usuário)

**Todos os 5 passos candidatos concluídos.** Próximas frentes naturais: camadas IBIS/QOC/Dung; refinar premissas/estimativas com dados reais; 2ª opinião por família de modelo real; empacotar o motor (PyPI).

---

## Como manter este registro
A cada marco relevante, adicione uma entrada datada na Linha do tempo (o quê / por quê / consequência), atualize o Snapshot e mova itens entre "em aberto" e "decidido". Os ciclos numerados em `cases/*/cycles/NNN-*.md` continuam sendo o registro fino por caso; este arquivo é a visão macro do projeto inteiro.
