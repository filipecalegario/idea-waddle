---
cycle: 002
slug: segunda-opiniao
phase: divergir          # divergir | convergir (ritmo Double Diamond)
opened: 2026-06-14
status: open
authored_by: "agent:revisor-2"
model: "claude-opus-4-8 (perspectiva diversa simulada)"
diversity_note: >
  SIMULAÇÃO de diversidade: esta revisão foi produzida pelo mesmo modelo da
  semeadura (claude-opus-4-8), adotando deliberadamente uma perspectiva
  diferente. NÃO é uma segunda família de modelo real. Substituir por uma
  revisão de outra família (GPT/Gemini/DeepSeek/Llama) quando possível — é
  exatamente o que o princípio de diversidade pede.
---

# Ciclo 002 — Segunda opinião (revisão crítica para diversidade)

## Por que este ciclo existe
O ciclo 001 foi semeado por um único agente/modelo (`agent:discovery`). O princípio de **diversidade** do projeto pede que outra voz conteste e amplie a caixa antes de qualquer convergência. Este ciclo adota uma perspectiva deliberadamente distinta — mais **cética quanto a capex, atenta a opex/sustentabilidade, a lock-in e a alternativas fora do "comprar GPU topo de linha"**.

## Vieses que identifico na semeadura (001)
1. **Foco em capex, pouco em opex.** A caixa estima custo de capital e energia, mas trata "comprar hardware" como premissa. Falta a pergunta anterior: **comprar vs. alugar vs. federar** com o Apuana / nuvem.
2. **Centrada em data center / topo de linha.** Ignora caminhos frugais (GPUs de consumo/refurbished) que mudam a ordem de grandeza do capex.
3. **Sustentabilidade ausente.** Energia aparecia só como custo (R$), não como **eficiência/impacto** — relevante para uma universidade pública.
4. **Diversidade de modelos como enfeite.** "Portfólio diverso" existe como opção, mas não há critério que premie pluralidade/soberania de forma explícita.
5. **Algumas restrições podem estar fortes/fracas demais** (ver contestações abaixo).

## Contribuições concretas incorporadas à caixa (rastreáveis)
- **Nova opção** em *Hardware de aceleração*: `GPUs de consumo / refurbished (RTX 4090/5090)` — capex baixíssimo, com ressalvas de ECC/NVLink, confiabilidade e licença. (`agent:revisor-2`)
- **Novo critério**: `Sustentabilidade / eficiência energética` (1-5), com escores semeados em refrigeração e hardware. (`agent:revisor-2`)
- **Novas restrições**: `GPUs de consumo × mercado chinês` (incompatível) e `GPUs de consumo × escala média` (alerta normativo). (`agent:revisor-2`)

## Divergências que proponho como Questões (ainda NÃO encodadas — p/ debate)
- **Q-A. Provisão:** adicionar um parâmetro `Modelo de provisão` = *on-prem / nuvem (cloud burst) / híbrido*? Isso reformula a caixa (muitas opções viram N/A em nuvem). Decisão de escopo — pode merecer um caso separado.
- **Q-B. Federação com o Apuana:** parte da inferência pode rodar no cluster existente em janelas ociosas? Vira opção de escala/provisão.
- **Q-C. Contestar `InfiniBand × Ascend = incompatível`:** há stacks RoCE/Ethernet para Ascend; talvez o correto seja *weak*, não *hard*. (camada de argumentação — futura)
- **Q-D. Contestar `ar × médio = weak`:** com GPUs de alto TDP em escala média, eu defenderia *incompatível* (hard). Divergência explícita entre `agent:discovery` e `agent:revisor-2`.
- **Q-E. Opex e prazo como critérios:** adicionar `custo operacional/ano` e `prazo até produção` ao QOC.
- **Q-F. Pegada de carbono:** matriz elétrica e PUE locais — sustentabilidade quantitativa, não só escore.

## Recomendação de processo
Antes de **convergir** (fechar caminhos para a diretoria), rodar **uma revisão por uma família de modelo realmente diferente** e abrir a chamada a humanos. Registrar quem (humano/modelo) sustenta cada divergência — a camada de argumentação (Dung) servirá para decidir quais sobrevivem.

> Este ciclo permanece **aberto** (modo divergir). As Questões Q-A..Q-F são candidatas a novos parâmetros/opções/critérios ou a argumentos na camada futura.
