---
cycle: 001
slug: abertura
phase: divergir          # divergir | convergir (ritmo Double Diamond)
opened: 2026-06-14
status: open
authored_by: "agent:discovery"
model: "claude-opus-4-8"
---

# Ciclo 001 — Abertura

## Propósito
Abrir a chamada pública e semear a **caixa morfológica** do cluster de inferência do CIn-UFPE com um conjunto inicial de parâmetros, opções e restrições — para que humanos e agentes comecem a divergir (propor alternativas) antes de convergir.

## Estado inicial semeado
Seis parâmetros, com opções de partida e restrições iniciais (CCA). Tudo proposto por `agent:discovery` (modelo `claude-opus-4-8`) — **propositalmente marcado como ponto de partida a ser questionado, não verdade**. O princípio de diversidade pede que outras vozes (humanas e de outros modelos) contestem e ampliem.

| Parâmetro | Opções semeadas |
|---|---|
| Hardware de aceleração | H100/H200 · L40S · MI300X · Ascend 910B |
| Origem de fornecimento | EUA · China · Parceria/doação |
| Software de serving | vLLM · SGLang · TensorRT-LLM · Ollama |
| Escala inicial | Nó único · Cluster pequeno · Cluster médio |
| Interconexão de rede | Ethernet · RoCE · InfiniBand |
| Modelo de acesso | API · Chat · Ambos |

Restrições iniciais em [`../morphology/constraints.yaml`](../morphology/constraints.yaml).

## Convites à divergência (o que falta)
- **Critérios de avaliação (QOC)** ainda não modelados: custo de capital, energia (kW e R$/mês), prazo de aquisição, soberania, capacidade (tokens/s), risco de fornecimento. → camada futura.
- **Estimativas quantitativas** por configuração.
- Parâmetros ausentes: **refrigeração/energia**, **armazenamento**, **modelo de financiamento**, **modelos de LLM a servir**, **políticas de uso/cota**.
- Diversidade de modelos: este ciclo foi semeado por um único modelo — **buscar segunda opinião de outra família de modelos** antes de convergir.

## Como contribuir neste ciclo
Abra um PR adicionando opções/parâmetros/restrições (ver [`/AGENTS.md`](../../../AGENTS.md)). O site vivo recalcula o espaço de soluções viável a cada contribuição.

## Critério para fechar o ciclo (convergir)
A definir com o usuário/comunidade — sugestão: quando houver ≥2 famílias de modelos e ≥2 contribuintes humanos representados, e os parâmetros essenciais (incluindo energia e financiamento) estiverem cobertos.
