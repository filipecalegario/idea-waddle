# Caso 0 · Cluster de inferência do CIn-UFPE

> Primeiro caso de uso da plataforma **idea-waddle**. Veja o contexto geral em [`/README.md`](../../README.md) e o protocolo em [`/AGENTS.md`](../../AGENTS.md).

## O problema

O Centro de Informática (CIn) da UFPE já opera o **Apuana**, um cluster *batch* focado em **treinamento**. Esta chamada propõe especificar, de forma colaborativa (humanos + agentes), uma infraestrutura voltada a **inferência** — incluindo o experimento de prover um **LLM para a comunidade universitária**.

O objetivo final é chegar a **caminhos de decisão** robustos e defensáveis — com estimativas de custo de capital, energia/mês e opções de aquisição de GPUs (mercado americano vs. chinês, fornecedores, parcerias) — para apresentar aos laboratórios e à diretoria do CIn, que podem financiar o cluster.

## Como este caso está organizado

```
cases/cin-ufpe-inference-cluster/
├── README.md            ← este arquivo
├── cycles/              ← linha do tempo (arquivos NNN-slug.md por ciclo)
│   └── 001-abertura.md
└── morphology/          ← a caixa morfológica viva
    ├── params/          ← um arquivo YAML por parâmetro (dimensão de decisão)
    └── constraints.yaml ← restrições de consistência (CCA) entre opções
```

## Caixa morfológica viva

Cada **parâmetro** (`morphology/params/*.yaml`) é uma dimensão de decisão; cada **opção** é um valor possível, com proveniência (quem/qual modelo propôs). O arquivo `constraints.yaml` registra **incompatibilidades** entre opções (Cross-Consistency Assessment — ver [`/docs/discovery/02-fundamentos-teoricos.md`](../../docs/discovery/02-fundamentos-teoricos.md)).

O motor em [`/engine/cca.py`](../../engine/cca.py) lê esses arquivos, poda as configurações inviáveis e gera o **site vivo** (a cada PR/merge, via GitHub Actions). Para rodar localmente:

```bash
pip install pyyaml
python engine/cca.py
# abra o site gerado em site/index.html
```

## Contribuindo

Abra um PR adicionando/editando um arquivo de parâmetro, uma opção ou uma restrição — seguindo o padrão de escrita do [`/AGENTS.md`](../../AGENTS.md). Toda contribuição registra sua proveniência.
