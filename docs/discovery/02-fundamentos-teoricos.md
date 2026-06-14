# Discovery 02 — Fundamentos teóricos

> **Status:** pesquisa inicial (Discovery)
> **Data:** 2026-06-14
> **Método:** varredura web + repositórios acadêmicos (arXiv, Semantic Scholar, DOI), com verificação de fontes.
> **Objetivo:** reunir os métodos que podem ser *implementados* na plataforma — a caixa morfológica e os frameworks de deliberação/argumentação.

---

## BLOCO A — Análise Morfológica Geral (Caixa Morfológica)

### A.1 — Método de Fritz Zwicky: General Morphological Analysis (GMA)

**O que é.** GMA é um método de estruturação de problemas multidimensionais e não-quantificáveis, criado pelo astrofísico Fritz Zwicky (Caltech, anos 1930–40). Em vez de otimizar uma função, ele *mapeia o espaço total de configurações possíveis* de um problema.

**Como se constrói a caixa morfológica (Zwicky box):**
1. Definir o problema e as características desejadas da solução.
2. Decompor o problema em **parâmetros** (dimensões/variáveis — ex.: "tipo de GPU", "origem de fornecimento", "topologia de rede", "modelo de financiamento").
3. Para cada parâmetro, listar um espectro discreto de **valores/opções** (estados que aquele parâmetro pode assumir).
4. Montar a matriz: cada parâmetro é uma coluna; seus valores ficam empilhados abaixo.
5. Uma **configuração** (solução candidata) = escolher exatamente um valor de cada parâmetro (um "caminho" pela caixa). O produto cartesiano dos valores é o *espaço de configurações* (que explode combinatorialmente).
6. Reduzir o espaço via **Cross-Consistency Assessment** (A.2).

**Por que serve ao nosso caso:** é não-quantificável (bom para decisão de infraestrutura com trade-offs políticos/econômicos), é auditável, e cada célula é nomeável — casa com rastreabilidade de quem propôs o quê.

**Referências:**
- Tom Ritchey, *General Morphological Analysis* — https://www.swemorph.com/pdf/gma.pdf
- Ritchey, *Fritz Zwicky, Morphologie and Policy Analysis* — https://www.researchgate.net/publication/267794873
- Visão geral — https://www.swemorph.com/ma.html · https://en.wikipedia.org/wiki/Morphological_analysis_(problem-solving)

**Implementação Git:** modele cada parâmetro como um arquivo (`params/01-gpu.yaml`, `params/02-fornecimento.yaml`), com lista de opções, cada uma com `id` estável, autor (vinculável ao Git blame/PR), data e justificativa. Um agente reconstrói a caixa a partir desses arquivos a cada PR e gera o site vivo. **A história do Git é o histórico da evolução da caixa.**

### A.2 — Cross-Consistency Assessment (CCA): modelagem de RESTRIÇÕES (ponto central)

**O que é.** CCA é o passo que torna a caixa morfológica útil: examina-se **cada par de valores** de dois parâmetros distintos e julga-se se podem coexistir. Pares incompatíveis "podam" todas as configurações que os contêm, reduzindo o espaço combinatório (muitas vezes a <1% do total) a um **espaço de soluções internamente consistente**.

**Como funciona:**
- Comparam-se apenas pares *entre* parâmetros diferentes (valores do mesmo parâmetro são mutuamente exclusivos por definição).
- Para n parâmetros, a matriz de CCA é triangular. Cada célula cruza um valor-A com um valor-B.
- Ritchey define **dois eixos** de julgamento:
  - **Tipo de restrição:** (1) *contradição lógica/formal* (impossível por definição), (2) *incompatibilidade empírica* (inviável no mundo real), (3) *restrição normativa* (indesejável por política/valores — ex.: viola política de compras da universidade).
  - **Grau de restrição:** força (ex.: totalmente incompatível vs. parcialmente). Na prática mais simples, binário: `OK` vs. `X`.
- Resultado: o conjunto de configurações sobreviventes (sem nenhum par marcado como incompatível) + o "solution space quotient" (% viável).

**Referência:**
- Tom Ritchey, *Principles of Cross-Consistency Assessment in General Morphological Modelling*, Acta Morphologica Generalis 4(2), 2015 — https://swemorph.wordpress.com/2015/12/07/principles-of-cross-consistency-assessment-in-morphological-modelling/ · cópia: https://archive.org/details/amg-4-2-2015

**Implementação Git (núcleo do sistema):** a restrição é uma relação entre dois `option.id`. Modele como arquivo de constraints (ver A.4); cada PR pode *adicionar* uma restrição ("isso não funciona com aquilo") sem tocar nos parâmetros. Um agente roda o CCA como função pura: dado o produto cartesiano menos os pares proibidos, retorna o espaço viável. Restrições normativas são especialmente relevantes (ex.: "GPU mercado chinês" × "exigência de suporte oficial local" pode ser normativamente conflitante).

### A.3 — Ferramentas digitais existentes para Morphological Analysis

| Ferramenta | Natureza | Notas |
|---|---|---|
| **MA/Carma** | Proprietária (Windows), Ritchey/SweMorph | Líder para GMA estendida com inferência "what-if". Não multiusuário. https://www.swemorph.com/macarma.html |
| **Parmenides EIDOS** | Proprietária | Inclui *Option Development* e análise visual de clusters. |
| **ACTIFELD / MEMIC / MORPHOL** | Proprietárias/acadêmicas | Pacotes clássicos de estruturação morfológica presencial. |
| **morphr** | **Aberta** (R/Shiny) | Implementação de MA em R, navegação interativa. Boa referência de UX. |

**Lacuna identificada (oportunidade):** a literatura registra que o software de MA existente "não fornece interface multiusuário, o que o torna impraticável para times distribuídos". **Nossa plataforma Git-native + site vivo preenche essa lacuna.**

**Referências:**
- *Towards Software Support for Collaborative Morphological Analysis* — https://www.researchgate.net/publication/346934057
- *Web-based software-support for collaborative morphological analysis in real-time* (Technological Forecasting & Social Change) — https://www.sciencedirect.com/science/article/abs/pii/S0040162517306637

> Nota: TRIZ usa uma matriz de contradições conceitualmente parecida (poda por incompatibilidade), mas não há ferramenta TRIZ aberta diretamente integrável; a conexão é metodológica.

### A.4 — Representação de dados para a caixa morfológica (YAML/JSON)

Proposta Git-friendly (arquivos pequenos, diffs legíveis, autoria rastreável): parâmetros e opções em arquivos separados; restrições em arquivo dedicado.

```yaml
# params/02-fornecimento.yaml
parameter:
  id: fornecimento
  label: "Origem de fornecimento das GPUs"
  options:
    - id: opt.fornecimento.us
      label: "Mercado americano (NVIDIA)"
      proposed_by: "@maria"        # rastreável via Git/PR
      pr: 42
      rationale: "Ecossistema CUDA maduro"
    - id: opt.fornecimento.cn
      label: "Mercado chinês"
      proposed_by: "agent:explorer-01"
      pr: 47
```

```yaml
# constraints.yaml  -> alimenta o CCA
constraints:
  - a: opt.fornecimento.cn
    b: opt.suporte.oficial_nvidia
    type: empirical            # logical | empirical | normative
    degree: incompatible       # incompatible | weak | ok
    by: "@joao"
    pr: 51
    note: "Suporte oficial NVIDIA local indisponível p/ via China"
```

O motor de CCA = produto cartesiano dos `options` por parâmetro, filtrando configurações que contenham qualquer par com `degree: incompatible`. Saída: lista de configurações viáveis + `solution_space_quotient`.

---

## BLOCO B — Frameworks de deliberação / argumentação colaborativa

### B.1 — IBIS e Dialogue Mapping (problemas perversos / wicked problems)

**O que é.** IBIS (Issue-Based Information System) foi criado por **Horst Rittel** (que cunhou "wicked problems") para problemas mal-estruturados de planejamento. Estrutura o diálogo em três tipos de nó: **Questões (Issues)**, **Ideias/Posições (Positions)** e **Argumentos (Pros/Cons)**. **Jeff Conklin** modernizou-o nos anos 1990 (gIBIS, QuestMap) e criou o **Dialogue Mapping** — captura de discussão não-estruturada em tempo real como grafo IBIS.

**Por que serve:** é o modelo canônico para "construir entendimento compartilhado sobre problemas perversos" — descreve exatamente a decisão de infraestrutura de cluster (múltiplos stakeholders, sem resposta única correta). É o framework de deliberação mais maduro e diretamente implementável.

**Referências:**
- Jeff Conklin, *Dialogue Mapping: Building Shared Understanding of Wicked Problems* (Wiley, 2005).
- CogNexus — http://www.cognexusgroup.com/wp-content/uploads/2013/07/Using-Dialogue-Mapping-to-Address-Wicked-Problems-05-23-2013.pdf
- Visão geral — https://www.lucidchart.com/blog/what-is-dialogue-mapping

**Implementação Git:** cada Issue = arquivo Markdown numerado (combina com `001-`, `002-`); Positions e Arguments = entradas estruturadas (front-matter YAML) referenciando o `id` da Issue. **IBIS é o "esqueleto da discussão"; a caixa morfológica é o "esqueleto da solução"** — eles se complementam (Issues → parâmetros; Positions → opções).

### B.2 — Design Rationale: QOC e modelo de Toulmin

**QOC (Questions, Options, Criteria).** MacLean, Young, Bellotti & Moran (1991), notação semiformal para *Design Space Analysis*: **Questões** (decisões) → **Opções** (respostas) → **Critérios** (dimensões de avaliação). Cada Opção liga-se a cada Critério com avaliação positiva/negativa. É a **ponte entre IBIS e a caixa morfológica**: Questões≈parâmetros, Opções≈valores, e adiciona **Critérios** explícitos — útil para chegar à "ideia robusta + estimativa de custo".
- DOI: 10.1207/s15327051hci0603&4_2 — https://dl.acm.org/doi/10.1207/s15327051hci0603%25264_2

**Modelo de Toulmin.** Estrutura argumentos em **Claim, Data/Grounds, Warrant, Backing, Qualifier, Rebuttal**. Útil para padronizar *como* um argumento (pro/con) num PR deve ser escrito — dá rigor ao "padrão de escrita".

**Implementação Git:** Critérios como arquivo compartilhado (`criteria.yaml`). Cada opção carrega avaliações por critério. Argumentos seguem template Toulmin no front-matter para serem parseáveis por agentes.

### B.3 — Geração e convergência de alternativas

- **Delphi method:** rodadas iterativas e **anônimas** de coleta de opinião de especialistas, com feedback agregado, convergindo a consenso. Mapeia em ciclos versionados (cada "round" = tag/milestone no Git).
- **Nominal Group Technique (NGT):** geração individual silenciosa → compartilhamento → discussão → **votação/priorização**. Permite divergência (incluindo *ideias híbridas*, análogas a merge) e convergência (ranking).
- **Double Diamond (British Design Council):** dois losangos de **divergir/convergir** (Descobrir→Definir | Desenvolver→Entregar). Dá o ritmo macro da chamada pública: fase divergente (abrir forks/opções) seguida de convergente (CCA + votação → caminhos de decisão).

**Referências:**
- *How to use the nominal group and Delphi techniques* — https://pmc.ncbi.nlm.nih.gov/articles/PMC4909789/
- Double Diamond — https://www.designcouncil.org.uk/our-resources/the-double-diamond/

**Implementação Git:** ciclos = milestones/tags numerados (casa com arquivos `001-`, `002-`). Votação via reações de PR/issues ou `votes.yaml` com autoria. O agente fecha cada ciclo gerando o snapshot da caixa + ranking.

### B.4 — Argument mapping e Computational Argumentation (Dung)

**Dung's Abstract Argumentation Frameworks (AAF).** Phan Minh Dung (1995): um AAF é um par **F = (A, R)**, A = argumentos (nós), R ⊆ A×A = relação de **ataque** (arestas dirigidas). Define semânticas de aceitabilidade (*conflict-free, admissible, preferred, grounded, stable*) que dizem **quais argumentos podem ser aceitos juntos**. É a base matemática para computar automaticamente "quais ideias sobrevivem ao debate".
- DOI: 10.1016/0004-3702(94)00041-X — https://www.sciencedirect.com/science/article/pii/000437029400041X
- **Bipolar AF** (acrescenta relação de **suporte** além de ataque) — https://arxiv.org/pdf/1707.09324

**AIF (Argument Interchange Format).** Padrão de intercâmbio de argumentos como grafo dirigido tipado: **I-nodes** (informação), **RA-nodes** (inferência/suporte), **CA-nodes** (conflito/ataque), **PA-nodes** (preferência). Tem reificações em RDF, Prolog e **JSON** — esquema pronto para serializar o grafo de debate no Git.
- DOI: 10.1017/S0269888906001044 — https://dl.acm.org/doi/10.1017/S0269888906001044

**Implementação Git:** debate como grafo — cada ideia/argumento = nó com `id`; relações `supports`/`attacks` apontando para outros `id` (estilo Bipolar AF, serializado em AIF-JSON). Um agente roda a semântica grounded/preferred para sugerir "conjunto de ideias mutuamente sustentáveis" — poda *argumentativa* análoga à poda *morfológica* do CCA. **Os dois motores (CCA sobre opções; AAF sobre argumentos) são complementares.**

### B.5 — Evolução / genealogia de ideias (fork/merge de ideias)

Não existe um "Git de ideias" canônico, mas há frameworks que justificam e modelam fork/merge conceitual:

- **Memética** (Dawkins, *The Selfish Gene*, 1976; Jack Balkin, *Cultural Software*): ideias como replicadores sujeitos a **herança, variação e seleção**. "Tradição" = linha de descendência memética — análoga a uma árvore de commits. Variação ≈ edição num fork; seleção ≈ merge/aceitação. https://jackbalkin.yale.edu/3-memetic-evolution
- **Conceptual Blending** (Fauconnier & Turner): novos conceitos surgem do **blend** de dois espaços mentais — modelo cognitivo do *merge de duas ideias*. https://handwiki.org/wiki/Philosophy:Conceptual_blending
- **Genealogia conceitual** (Matthieu Queloz, *The Practical Origins of Ideas*, Oxford, 2021): uma ideia se **diferencia numa família** conforme as necessidades mudam — base teórica para *branching* de conceitos. https://academic.oup.com/book/39497
- Trabalho recente: *A hybrid marketplace of ideas* — https://arxiv.org/pdf/2501.02132 · Rethinking version control for agents — https://pepicrft.me/blog/rethinking-version-control-for-agents/

**Implementação Git:** o Git já fornece a árvore de descendência (branches = forks de ideia; merge commits = blends; `git blame`/autor = atribuição). Acrescente metadados explícitos por ideia (`lineage: parents: [id1, id2]`) para reconstruir uma **árvore genealógica de ideias** independente da topologia de arquivos. Combine com arquivos numerados `001-`, `002-` por ciclo (snapshots) para ter *genealogia* (contínua) e *marcos* (discretos).

---

## Síntese: como os blocos se encaixam (três camadas no repositório)

1. **Camada de discussão (B.1/B.2):** IBIS/Dialogue Mapping + QOC estruturam *como* Questões, Opções e Argumentos entram via PR. Issues IBIS → parâmetros; Positions → opções; Critérios QOC → avaliação.
2. **Camada de solução (Bloco A):** a caixa morfológica agrega as opções; o **CCA** poda configurações inviáveis (logical/empirical/normative). É o "site vivo da caixa".
3. **Camada de raciocínio automático (B.4):** Dung AAF / Bipolar AF + AIF-JSON computam quais *argumentos* (suporte/ataque) sobrevivem — poda argumentativa paralela à morfológica.

O **ritmo de ciclos** vem do Double Diamond / Delphi / NGT (divergir→convergir, rodadas numeradas); a **memética + Git** dão a genealogia fork/merge com autoria rastreável.

**Padrões serializáveis para reusar (não reinventar a roda):** **YAML** para parâmetros/opções/restrições (diffs legíveis), **AIF (JSON)** para o grafo de argumentação, **IBIS** como vocabulário dos nós de discussão. Os dois motores a implementar: (a) **CCA** sobre o produto cartesiano de opções e (b) **semântica grounded de Dung** sobre o grafo de argumentos.

---

## Fontes
GMA — swemorph.com/pdf/gma.pdf · swemorph.com/ma.html · CCA (Ritchey 2015) — swemorph.wordpress.com · archive.org/details/amg-4-2-2015 · MA/Carma — swemorph.com/macarma.html · MA colaborativa — sciencedirect.com/.../S0040162517306637 · researchgate 346934057 · IBIS/Dialogue Mapping — cognexusgroup.com · QOC — DOI 10.1207/s15327051hci0603&4_2 · Dung AAF — DOI 10.1016/0004-3702(94)00041-X · Bipolar AF — arXiv 1707.09324 · AIF — DOI 10.1017/S0269888906001044 · Delphi/NGT — PMC4909789 · Double Diamond — designcouncil.org.uk · Memética — jackbalkin.yale.edu · Queloz — academic.oup.com/book/39497 · arXiv 2501.02132

> **Nota de verificação:** DOIs de Dung, QOC e AIF confirmados nas buscas. O PDF do GMA (swemorph) existe mas é binário; conteúdo metodológico corroborado por fontes secundárias. Double Diamond incluído por conhecimento estabelecido.
