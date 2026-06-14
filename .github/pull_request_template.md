<!--
Protocolo de colaboração idea-waddle (ver AGENTS.md).
Humanos e agentes contribuem por PR. Agentes PROPÕEM; um humano RATIFICA o merge.
-->

## Tipo de contribuição
<!-- marque com [x] -->
- [ ] Nova ideia / opção (em um parâmetro existente)
- [ ] Novo parâmetro (nova dimensão de decisão)
- [ ] Bifurcação de ideia (*fork* — registra `lineage.parents`)
- [ ] Mesclagem de ideias (*merge* / blend — credita todos os pais)
- [ ] Restrição (CCA) — incompatibilidade entre opções
- [ ] Argumento (pró/contra uma ideia ou restrição)
- [ ] Critério de avaliação (QOC) / estimativa
- [ ] Ciclo (linha do tempo) / outro

## Resumo
<!-- O que muda e por quê. Uma ideia robusta nasce do debate: seja explícito. -->

## Proveniência (rastreabilidade — obrigatório)
- Autor: <!-- @usuario  ou  agent:nome -->
- Se agente, modelo + versão: <!-- ex.: claude-opus-4-8 -->

## Diversidade
<!-- Esta contribuição amplia a pluralidade de visões/modelos? Há risco de uma só
voz dominar? Buscou-se segunda opinião de outra família de modelos? -->

## Checklist
- [ ] Segui o **padrão de escrita** do [`AGENTS.md`](../AGENTS.md) (front-matter, ids estáveis).
- [ ] Rodei o linter localmente: `python engine/lint.py` (e/ou a CI está verde).
- [ ] Registrei a **proveniência** (quem / qual modelo).
- [ ] Não sobrescrevi autoria alheia; conflitos/mesclas estão explicitados.
- [ ] Se for um marco do projeto, atualizei [`docs/spec/00-evolucao.md`](../docs/spec/00-evolucao.md).

> Lembrete: nenhum PR é mesclado automaticamente. Um humano responsável revisa e **ratifica** (CODEOWNERS).
