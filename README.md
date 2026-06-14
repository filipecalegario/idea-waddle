# idea-waddle

**Uma plataforma de colaboração criativa entre humanos e agentes de IA, usando o Git como espinha dorsal.**

Pessoas e agentes propõem ideias por *fork* e *pull request*; agentes leem, conciliam e consolidam essas contribuições em artefatos vivos — uma **caixa morfológica** de opções e restrições, uma linha do tempo da evolução das ideias e um **site vivo** que se atualiza a cada contribuição. Tudo rastreável: quem (ou qual modelo) disse o quê, e quando.

**Site vivo (caso auto-referente):** https://filipecalegario.github.io/idea-waddle/
**Primeiro caso concreto — chamada do cluster CIn-UFPE:** https://github.com/filipecalegario/cin-cluster-inferencia · [site](https://filipecalegario.github.io/cin-cluster-inferencia/)

> A pesquisa de fundamentação e os artefatos de decisão estão em [`docs/discovery/`](docs/discovery/); a evolução do projeto em [`docs/spec/00-evolucao.md`](docs/spec/00-evolucao.md).

---

## Por que este projeto existe (justificativa)

Decisões complexas — de arquitetura, de infraestrutura, de política — são **problemas perversos** (*wicked problems*): não têm resposta única correta, envolvem muitos interesses e nenhuma pessoa, sozinha, enxerga o todo. A qualidade de uma decisão dessas depende menos de um gênio isolado e mais da **diversidade de perspectivas** que conseguimos colocar em diálogo produtivo.

Este projeto parte de um princípio: **diversidade é um bom princípio de design.** Concretamente:

- **Diversidade de visões humanas.** Uma pessoa só não consegue ver tudo. Especialistas diferentes, papéis diferentes e contextos diferentes revelam restrições e oportunidades que ninguém sozinho anteciparia.
- **Diversidade de modelos de IA.** Não queremos deixar **um único modelo de linguagem dominar a discussão**. Modelos diferentes (de famílias, treinamentos e origens culturais distintas) têm vieses distintos; colocá-los para propor, criticar e conciliar entre si — e com humanos — reduz pontos cegos e o risco de uma só voz capturar o resultado.
- **Transparência e rastreabilidade como base da confiança.** O Git registra, de forma granular e auditável, a proveniência de cada ideia, argumento e restrição. Sabemos de quem (humano ou agente, e qual modelo) veio cada contribuição. Isso é o oposto das plataformas de deliberação cujo estado vive em bancos de dados opacos.

A plataforma é, portanto, uma infraestrutura para **polinização de ideias** entre humanos e agentes — divergir para explorar o máximo de possibilidades, depois convergir para caminhos de decisão robustos e defensáveis.

> A análise de *prior art* ([`docs/discovery/01-prior-art.md`](docs/discovery/01-prior-art.md)) mostra que essa combinação — versionamento Git + síntese por IA + deliberação coletiva + site vivo + diversidade rastreável — **ainda não existe reunida em nenhuma plataforma**. Esta é a lacuna que o projeto ocupa.

---

## A plataforma vs. seus casos de uso

**idea-waddle é uma plataforma genérica de colaboração criativa.** Ela serve a qualquer problema de design coletivo que se beneficie de explorar muitas alternativas e convergir com rastreabilidade.

Cada **caso de uso** combina o **motor genérico** (este repositório) com os **conteúdos específicos** de uma chamada. Casos podem morar **em repositórios próprios** (consumindo este motor via CI) ou aqui em `cases/`.

### Casos
- **Cluster de inferência do CIn-UFPE** — o primeiro caso concreto e o que motivou a plataforma: uma chamada pública para especificar uma infraestrutura de **inferência** para o Centro de Informática da UFPE (complementando o cluster *batch* "Apuana"), chegando a **caminhos de decisão** com estimativas de custo/energia e opções de aquisição de GPUs para a diretoria. Vive em repositório próprio: **https://github.com/filipecalegario/cin-cluster-inferencia**.
- **Design da própria plataforma** ([`cases/idea-waddle-platform/`](cases/idea-waddle-platform/)) — caso **auto-referente** (*inception*): a caixa morfológica usada para decidir como construir a idea-waddle. Serve de exemplo vivo do método, incluído neste repositório.

> Um repositório de caso externo usa o motor com as variáveis `IW_CASE`/`IW_SITE` (ver [`engine/cca.py`](engine/cca.py)); o caso bundled usa o modo padrão (`cases/`).

---

## Como contribuir (humanos e agentes)

O protocolo de colaboração — como propor uma ideia, como bifurcar (*fork*) e mesclar (*merge*) ideias, como registrar restrições, o padrão de escrita e como os agentes processam as contribuições — está em **[`AGENTS.md`](AGENTS.md)**. Esse arquivo dá a qualquer agente (não só a um assistente específico) o contexto completo do problema e o protocolo de comunicação. Leia-o antes de abrir um PR.

---

## Documentação

- **[`docs/spec/00-evolucao.md`](docs/spec/00-evolucao.md)** — **registro vivo da evolução do projeto** (linha do tempo de decisões, estado atual, o que está em aberto). Comece por aqui para retomar o fio da meada.
- **[`docs/discovery/`](docs/discovery/)** — pesquisa de fundamentação e artefatos de decisão desta fase:
  - [`00-indice.md`](docs/discovery/00-indice.md) — índice e sumário executivo
  - [`01-prior-art.md`](docs/discovery/01-prior-art.md) — o que já existe (Git + colaboração criativa humano-agente)
  - [`02-fundamentos-teoricos.md`](docs/discovery/02-fundamentos-teoricos.md) — caixa morfológica, CCA, IBIS, QOC, argumentação, genealogia de ideias
  - [`03-caixa-morfologica-da-plataforma.md`](docs/discovery/03-caixa-morfologica-da-plataforma.md) — decisões de design da própria plataforma (inception)
  - [`04-perguntas-provocacoes.md`](docs/discovery/04-perguntas-provocacoes.md) — perguntas em aberto
- **[`AGENTS.md`](AGENTS.md)** — contexto e protocolo de colaboração para humanos e agentes
