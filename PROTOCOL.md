# Protocolo de colaboração idea-waddle

> Protocolo **canônico e agnóstico de caso** para colaboração criativa entre humanos e agentes sobre Git. Esta é a *capacidade* ("como colaborar"), separada do *contexto* de cada caso. É a **fonte única**: o arquivo vive em `idea-waddle/PROTOCOL.md` e é **embutido no `AGENTS.md` de cada repositório** (de caso ou da plataforma) por `engine/sync_protocol.py`, para que qualquer repo seja autossuficiente ao clonar — qualquer agente (Claude, Codex, Gemini…) ou humano lê tudo localmente, sem depender de link remoto.

## 1. Princípios (não negociáveis)
1. **Diversidade.** Pluralidade de visões humanas e de modelos de IA. **Nenhum modelo único deve dominar.** Quando possível, ideias e sínteses passam por mais de uma família de modelos.
2. **Rastreabilidade.** Toda contribuição registra proveniência: quem (humano `@usuario` ou agente `agent:nome`) e — para agentes — **qual modelo e versão**. O Git é a fonte de verdade da autoria.
3. **Human-in-the-loop.** Agentes **propõem**; humanos **ratificam**. Nenhum PR é mesclado automaticamente.
4. **Divergir, depois convergir.** Primeiro abrir o máximo de possibilidades; depois consolidar em caminhos de decisão.
5. **As ideias não se apagam, evoluem.** Em vez de deletar uma opção, marque `status: superseded` (ou `rejected`) com `reason:` (e opcional `superseded_by:`). Ela continua **visível e riscada**, com o motivo, mas **sai do cálculo**. A evolução completa (o que entrou/saiu, por quê, quando) aparece no **mapa de evolução** gerado do histórico do Git.

## 2. Como contribuir

### Fluxo
1. **Fork** do repositório (ou branch, se você tem acesso).
2. Edite/adicione arquivo(s) estruturado(s) em `morphology/` (ou um ciclo em `cycles/`).
3. Abra um **Pull Request** descrevendo a intenção (nova ideia? bifurcação? merge? restrição? argumento?).
4. A CI valida o formato (lint). Um ou mais agentes podem ler o PR e propor a consolidação.
5. Um humano **ratifica** o merge. O site vivo se atualiza.

### Tipos de contribuição
- **Nova opção** — adiciona uma opção a um parâmetro da caixa morfológica.
- **Novo parâmetro** — nova dimensão de decisão.
- **Bifurcação (*fork* de ideia)** — variante de uma ideia existente (`lineage.parents`).
- **Mesclagem (*merge* de ideias)** — combina ideias num *blend* (credita todos os pais).
- **Restrição (CCA)** — duas opções incompatíveis (lógica / empírica / normativa). Pode ser contestada por argumento.
- **Argumento** — pró/contra uma opção (ou restrição), de preferência com evidência e justificativa.

## 3. Padrão de escrita
Contribuições usam **YAML** com `id` estável e referenciável e **proveniência obrigatória**. Exemplo de opção (em `morphology/params/NN-*.yaml`):

```yaml
- id: opt.<parametro>.<slug>
  label: "Rótulo curto"
  proposed_by: "@usuario"        # ou agent:nome
  model: "claude-opus-4-8"       # OBRIGATÓRIO se agente (rastreabilidade)
  status: proposed               # proposed | accepted | superseded | rejected
  rationale: "Por que esta opção."
  scores: { criterio_id: 4 }     # 1-5, opcional (camada QOC)
  estimates: { campo: 123 }      # numérico, opcional (camada de métricas)
```

## 4. As camadas (todas no motor; cada caso usa o que precisar)
1. **Solução — caixa morfológica + CCA** (`params/*.yaml`, `constraints.yaml`): opções por dimensão; o motor poda configurações inviáveis. Restrição liga opções de parâmetros **diferentes**:
   ```yaml
   # constraints.yaml
   constraints:
     - a: opt.x.a
       b: opt.y.b
       type: empirical            # logical | empirical | normative
       degree: incompatible       # incompatible | weak (só 'incompatible' poda)
       by: "@usuario"             # ou agent:nome (+ model se agente)
       note: "Por quê."
   ```
2. **Avaliação — QOC** (`criteria.yaml` + `scores`/`estimates`): critérios qualitativos (com `weight` e `short` opcionais) e matriz opções × critérios. **Estimativas quantitativas são genéricas:** o caso declara fórmulas em `morphology/metrics.yaml`; o motor soma os campos `estimates` das opções + constantes (`assumptions.yaml`) e avalia cada expressão (sem domínio embutido):
   ```yaml
   # metrics.yaml
   metrics:
     - id: capex
       label: "Custo de capital"
       expr: "n_gpus * capex_per_gpu_brl + capex_fixed_brl"   # nomes = estimates somados + assumptions + métricas anteriores
       format: brl            # brl | int | number | number1
       requires: [n_gpus, capex_per_gpu_brl]
       missing: "selecione hardware + escala"
   ```
3. **Discussão — IBIS** (`arguments.yaml`): cada parâmetro é uma Questão; opções são Posições; argumentos `pro`/`con` (com `target` numa opção):
   ```yaml
   # arguments.yaml
   arguments:
     - id: arg.<slug>
       target: opt.<param>.<slug>
       stance: pro | con
       claim: "Afirmação curta."
       by: "@usuario"             # ou agent:nome (+ model se agente)
       attacks: [arg.<outro>]     # opcional: refuta outro argumento
   ```
4. **Argumentação — Dung** (`attacks`): refutações formam um grafo; o motor calcula a **extensão grounded** (quais argumentos sobrevivem). Análogo argumentativo do CCA.

## 5. Validação (lint)
O padrão é verificado por `engine/lint.py` (roda na CI a cada PR). Rode localmente antes do PR:
```bash
# repo com casos em cases/:        python engine/lint.py
# repo de um caso só (morphology/ na raiz):  IW_CASE="$PWD" python <caminho>/engine/lint.py
```
Valida: ids únicos e referências existentes; restrições entre parâmetros **diferentes**; `degree`/`type`/`status`/`kind` válidos; **rastreabilidade** (agente sem `model` é erro); `scores` em 1–5; front-matter dos ciclos; `arguments`/`metrics`. Erros (✗) bloqueiam o merge; avisos (⚠) não.

## 6. Como agentes devem processar contribuições
1. **Validar formato** (front-matter, ids únicos, referências existentes).
2. **Identificar o tipo** e onde encaixa (parâmetro/opção/restrição/argumento/métrica).
3. **Conciliar com o estado atual** — detectar duplicatas/conflitos e oportunidades de *blend*; **não sobrescrever autoria alheia**.
4. **Rodar os motores** quando aplicável (CCA sobre opções; Dung sobre argumentos).
5. **Propor via PR — nunca mesclar sozinho.** Registrar a proveniência da própria ação.
6. **Preservar diversidade** — sinalizar quando uma só voz domina; buscar 2ª opinião de outra família de modelos antes de consolidar.

## 7. Linha do tempo / ciclos
A evolução é organizada em ciclos `cycles/NNN-slug.md` (front-matter YAML: `cycle`, `slug`, `status`, `authored_by`, e `model` se agente). Marcos discretos + o histórico do Git reconstroem a genealogia das ideias (forks/merges).
