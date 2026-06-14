# AGENTS.md — Contexto e protocolo de colaboração

> Este arquivo dá a **qualquer agente** (e a qualquer humano) o contexto do problema e o protocolo para contribuir. É deliberadamente mais abstrato e portável que instruções de um assistente específico — segue o padrão emergente [AGENTS.md](https://agents.md/) para repositórios *agent-native*.
>
> **Status:** rascunho de Discovery. O protocolo abaixo é uma proposta de partida e está sujeito a deliberação pela própria plataforma. Decisões em aberto: [`docs/discovery/04-perguntas-provocacoes.md`](docs/discovery/04-perguntas-provocacoes.md).

## 1. O que é este repositório

Uma **plataforma de colaboração criativa entre humanos e agentes**, com o **Git como espinha dorsal**. Aqui não se versiona código de um programa — versiona-se um **conjunto de ideias** sobre um problema. Contribuintes (humanos e agentes) propõem, bifurcam (*fork*) e mesclam (*merge*) ideias; agentes leem as contribuições e as consolidam em artefatos vivos (caixa morfológica, linha do tempo, site vivo).

Leia o contexto completo no [`README.md`](README.md) e a fundamentação em [`docs/discovery/`](docs/discovery/).

## 2. Princípios (não negociáveis)

1. **Diversidade.** Buscamos pluralidade de visões humanas e de modelos de IA. **Nenhum modelo único deve dominar** a discussão. Quando possível, ideias e sínteses passam por mais de uma família de modelos.
2. **Rastreabilidade.** Toda contribuição registra sua proveniência: quem (humano `@usuario` ou agente `agent:nome`), e — para agentes — **qual modelo e versão**. O Git é a fonte de verdade da autoria.
3. **Human-in-the-loop.** Agentes **propõem**; humanos **ratificam**. Nenhum PR é mesclado automaticamente sem aprovação humana. (Lição dos incidentes de "AI maintainer" — ver [`01-prior-art.md`](docs/discovery/01-prior-art.md).)
4. **Divergir, depois convergir.** Primeiro abrimos o máximo de possibilidades; depois consolidamos em caminhos de decisão (ritmo Double Diamond).
5. **As ideias não se apagam, evoluem.** Preferimos *supersedência* (uma nova versão substitui a antiga, com histórico preservado) a deleção silenciosa.

## 3. Como contribuir

### Fluxo geral
1. **Fork** do repositório (ou branch, se você tem acesso).
2. Faça sua contribuição como **arquivo(s) Markdown estruturado(s)** (ver §4).
3. Abra um **Pull Request** descrevendo a intenção: nova ideia? bifurcação? merge? restrição?
4. Um ou mais agentes leem o PR, verificam o formato, conciliam com o estado atual e propõem a incorporação na caixa morfológica.
5. Um humano revisa e ratifica o merge.

### Tipos de contribuição
- **Nova ideia / opção** — adiciona uma opção a um parâmetro da caixa morfológica.
- **Novo parâmetro** — introduz uma nova dimensão de decisão.
- **Bifurcação (*fork* de ideia)** — deriva uma variante de uma ideia existente (registra `lineage.parents`).
- **Mesclagem (*merge* de ideias)** — combina duas ou mais ideias num *blend* (registra todos os pais e credita os autores).
- **Restrição (CCA)** — afirma que duas opções são incompatíveis (lógica / empírica / normativa). Restrições podem ser contestadas via argumento.
- **Argumento** — pró ou contra uma ideia/restrição (de preferência no formato Toulmin: afirmação + evidência + justificativa).

## 4. Padrão de escrita (proposta inicial)

Contribuições estruturadas usam **front-matter YAML + corpo Markdown**. IDs são estáveis e referenciáveis. Exemplo de uma opção:

```yaml
---
type: option            # option | parameter | constraint | argument | idea
id: opt.fornecimento.cn
parameter: fornecimento
label: "GPUs do mercado chinês"
proposed_by: "agent:explorer-01"
model: "claude-opus-4-8"   # obrigatório p/ agentes: modelo + versão
lineage:
  parents: []           # ids das ideias-mãe, se for fork/merge
status: proposed        # proposed | accepted | superseded | rejected
---

## Resumo
Adquirir GPUs do mercado chinês (ex.: Huawei Ascend 910B).

## Justificativa
...

## Argumentos relacionados
- arg.123 (pró), arg.456 (contra)
```

Esquemas detalhados de parâmetros, opções, restrições e argumentos estão exemplificados em [`02-fundamentos-teoricos.md`](docs/discovery/02-fundamentos-teoricos.md) (§A.4 e §B).

> Quando o repositório amadurecer, o CI poderá validar (lint) o formato dos PRs automaticamente.

## 5. Como os agentes devem processar o conteúdo

Ao ler um PR, um agente deve:
1. **Validar formato** (front-matter presente, IDs únicos, referências existentes).
2. **Identificar o tipo** de contribuição e onde ela encaixa (parâmetro/opção/restrição/argumento).
3. **Conciliar com o estado atual** — detectar duplicatas, conflitos e oportunidades de *blend*; não sobrescrever autoria alheia.
4. **Rodar os motores de consolidação** quando aplicável:
   - **CCA** sobre as opções (poda configurações inviáveis; recalcula o espaço de soluções viável);
   - **semântica de argumentação (Dung)** sobre o grafo de suporte/ataque, quando houver.
5. **Atualizar os artefatos vivos** (caixa morfológica, linha do tempo) e propor a mudança via PR — **nunca mesclar sozinho**.
6. **Registrar proveniência** da própria ação (qual agente/modelo fez a consolidação).
7. **Preservar diversidade** — sinalizar quando uma só voz (humana ou de um modelo) está dominando; quando possível, buscar uma segunda opinião de outro modelo antes de consolidar.
8. **Atualizar o registro de evolução** ([`docs/spec/`](docs/spec/)) quando a contribuição representar um marco do projeto (ver §7).

## 6. Linha do tempo / ciclos

A evolução das ideias é organizada em ciclos, com arquivos numerados no padrão `NNN-slug.md` (ex.: `001-abertura.md`, `002-...`). Isso dá marcos discretos legíveis; combinado com o histórico do Git (genealogia contínua via branches/merges), reconstrói tanto a *árvore genealógica das ideias* quanto a *sequência de marcos*.

## 7. Registro de evolução do projeto (`docs/spec/`)

A pasta [`docs/spec/`](docs/spec/) guarda o **registro vivo da evolução do projeto** — a visão macro do "fio da meada": linha do tempo das decisões (o quê / por quê / consequência), estado atual, decisões em aberto e próximos passos. O arquivo principal é [`docs/spec/00-evolucao.md`](docs/spec/00-evolucao.md).

**Esta pasta deve ser SEMPRE mantida atualizada conforme o projeto evolui.** A cada marco relevante — nova decisão, nova capacidade, mudança de rumo, fechamento de ciclo — humanos e agentes devem registrar uma entrada datada (data absoluta AAAA-MM-DD), atualizar o snapshot de estado atual e mover itens entre "em aberto" e "decidido". Manter este registro em dia é parte do trabalho, não um extra.

> Distinção: `docs/spec/` é a visão **macro** de todo o projeto; os ciclos em `cases/*/cycles/NNN-*.md` (§6) são o registro **fino** por caso. Ambos evoluem juntos.

## 8. Casos de uso

A plataforma é genérica. Conteúdos específicos de cada chamada ficam (à medida que o projeto evolui) em `cases/`. O primeiro caso é o cluster de inferência do CIn-UFPE (ver [`README.md`](README.md)).
