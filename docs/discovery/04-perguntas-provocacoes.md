# Discovery 04 — Provocações: perguntas para ampliar o espaço de ideias

> **Status:** aberto (Discovery)
> **Data:** 2026-06-14
> **Objetivo:** você pediu que eu te provocasse com perguntas para ampliar as possibilidades. Estão agrupadas por tema. Não precisam ser respondidas todas agora — várias são, elas mesmas, candidatas a virarem Questões (IBIS) dentro da plataforma.

## A. Sobre a natureza da plataforma (a "espinha dorsal")
1. A plataforma é **genérica** (qualquer problema de design coletivo) e o cluster da UFPE é só o **primeiro caso**, ou o cluster é o produto e a plataforma é meio? → *(você já respondeu: é genérica; cluster é um caso de uso — ver README)*
2. O "fork de ideia" é literalmente um fork do Git, ou uma **bifurcação conceitual** registrada por metadados (`lineage`) dentro do mesmo repositório? Os dois têm UX e custos muito diferentes.
3. Quando duas ideias "mergeiam", quem escreve a síntese — um agente, o autor humano, ou um par humano+agente? E como se credita a autoria do *blend*?
4. Soberania de dados: para a UFPE/CIn, faz diferença o conteúdo morar no GitHub (EUA) vs. GitLab self-hosted? Isso é uma restrição normativa real?

## B. Sobre diversidade (o princípio central)
5. Como **medir** diversidade de forma rastreável? (nº de famílias de modelos? entropia de opiniões? proporção humano:agente por ciclo?)
6. O que impede um único modelo (ou uma única pessoa influente) de **dominar** a caixa morfológica? Quorum? Cotas? Anonimização estilo Delphi em certas fases?
7. Diversidade pode gerar **incoerência**. Qual o limite entre "pluralidade saudável" e "caos"? Quem/o quê decide quando convergir? (Double Diamond dá um ritmo — basta?)
8. Devemos buscar diversidade **de modelos** (Claude, GPT, Gemini, Llama, modelos chineses...) deliberadamente, inclusive para evitar viés cultural/geopolítico — especialmente relevante num projeto que decide comprar GPUs "do mercado americano ou chinês"?

## C. Sobre a caixa morfológica viva
9. A caixa deve mostrar **apenas o estado atual** ou também a **animação histórica** (como as opções/restrições nasceram e morreram ao longo dos PRs)?
10. Restrições (CCA) podem ser **contestadas**? Se alguém diz "X é incompatível com Y" e outro discorda, isso vira um argumento (Dung) sobre a própria restrição?
11. Quando o espaço de soluções viável fica pequeno demais (super-restringido) ou grande demais, o que a plataforma faz? Sinaliza? Sugere relaxar restrições?
12. A caixa morfológica deve carregar **estimativas quantitativas** por configuração (custo de capital, kW, R$/mês de energia, prazo de aquisição), ou isso fica num artefato separado conectado às células?

## D. Sobre governança e confiança
13. Como evitar os incidentes de "AI maintainer" (spam de PRs, comportamento adversarial)? Rate-limiting por agente? Allowlist? Reputação?
14. Agentes têm **identidade verificável**? (qual modelo, qual operador humano por trás, qual versão do prompt?) Isso entra na proveniência?
15. Há contribuições que **só humanos** podem fazer (ex.: ratificar uma decisão final, aprovar orçamento)? Onde fica a fronteira?
16. O "padrão de escrita" deve ser **imposto por template/lint** (CI rejeita PR mal formatado) ou apenas recomendado?

## E. Sobre o resultado final (para a diretoria do CIn)
17. O entregável final é **um** caminho recomendado, ou **N caminhos** com trade-offs (a diretoria escolhe)? A caixa morfológica favorece o segundo.
18. Quais **critérios de avaliação** (QOC) importam para os decisores: custo total, custo/mês de energia, soberania, prazo, capacidade de inferência (tokens/s), risco geopolítico de fornecimento, manutenção/suporte?
19. O projeto deve produzir, além das ideias, uma **estimativa defensável** (planilha viva com fontes de preço/energia)? Isso é parte da plataforma ou anexo?
20. Como a plataforma demonstra seu próprio valor — o fato de ter sido construída/decidida *por ela mesma* (inception) é parte da narrativa para a diretoria?

## F. Meta / pesquisa
21. Vale contatar/forkar **Talk to the City** (síntese LLM open-source) e **Log4brains** (Git→site vivo) como base, em vez de construir do zero?
22. Há interesse em publicar isto como **artigo** (a lacuna identificada no Discovery 01 é real e citável)? Isso muda o rigor de instrumentação/rastreabilidade desde já.
