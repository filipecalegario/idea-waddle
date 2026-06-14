# Caso auto-referente · design da plataforma idea-waddle

> A plataforma analisando a si mesma (*inception*): a caixa morfológica usada para decidir **como construir a idea-waddle**. Serve de **exemplo vivo** do método e demonstra a ferramenta com o próprio caso dela.

## Origem
Semeado a partir de [`/docs/discovery/03-caixa-morfologica-da-plataforma.md`](../../docs/discovery/03-caixa-morfologica-da-plataforma.md). São 9 parâmetros de design (substrato, unidade de contribuição, artefato de síntese, motor de consolidação, site vivo, protocolo de contexto, governança, diversidade, granularidade do ciclo).

## Estrutura
```
morphology/
├── params/          ← um YAML por parâmetro de design
├── constraints.yaml ← restrições (CCA) entre opções
└── criteria.yaml    ← critérios (alcance, soberania, simplicidade)
cycles/
└── 001-abertura.md
```

## Outros casos
O primeiro caso concreto (cluster de inferência do CIn-UFPE) vive em um repositório
próprio: **https://github.com/filipecalegario/cin-cluster-inferencia** (consome este
mesmo motor via CI). Veja o protocolo em [`/AGENTS.md`](../../AGENTS.md).
