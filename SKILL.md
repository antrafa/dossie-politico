---
name: dossie-politico
description: "Investigate Brazilian politicians and public officials, audit official transparency portals (Câmara, Senado, TSE, CGU, Portais Estaduais/Municipais), legislative productivity, attendance, proposals, expenses, salary, asset declarations, and compile a chronological dossier of investigations, news, and controversies into a standalone interactive HTML dashboard in ~/.dossie-politico/<nome_politico>.html with an automatically updated catalog in ~/.dossie-politico/index.html."
trigger: /dossie-politico
---

# /dossie-politico

Audita e consolida um dossiê completo de transparência pública sobre qualquer agente político brasileiro, cobrindo dados cadastrais, remuneração oficial, cotas e gastos públicos, atividade legislativa (projetos e assiduidade), evolução patrimonial declarada no TSE e histórico de investigações, notícias e escândalos com contraditório e fontes auditáveis.

Ao final, grava o relatório em formato HTML na pasta oculta **`~/.dossie-politico/<nome_do_politico>.html`** e atualiza automaticamente o painel de índice geral em **`~/.dossie-politico/index.html`**.

---

## Estrutura de Arquivos da Skill

- `scripts/run_dossier.py`: Orquestrador principal da extração, geração e atualização do índice.
- `scripts/fetch_camara.py`: Coleta automatizada na API da Câmara dos Deputados.
- `scripts/fetch_senado.py`: Coleta automatizada na API do Senado Federal.
- `scripts/fetch_tse_transparency.py`: Suporte a consultas eleitorais e patrimoniais do TSE.
- `scripts/generate_dossier_html.py`: Motor de renderização dos relatórios individuais e do `index.html`.
- `references/sources-guide.md`: Guia de endpoints oficiais, portais e dorks de busca.
- `references/dossier-schema.md`: Esquema JSON formal do dossiê.
- `references/legal-journalism-ethics.md`: Diretrizes de rigor jurídico, neutralidade e contraditório.

---

## Procedimento de Execução (Passo a Passo)

Siga rigorosamente as etapas abaixo em ordem cronológica. Cada passo possui critério de conclusão verificável antes de avançar para o seguinte.

### Passo 1 — Identificação do Agente Político e Esfera de Atuação

1. Identifique o nome completo e o nome eleitoral da pessoa pública fornecida pelo usuário.
2. Determine o cargo atual e os mandatos pregressos (ex: Deputado Federal, Senador, Governador, Prefeito, Deputado Estadual, Ministro).
3. Identifique o partido político, estado de representação (UF) e o período da legislatura/mandato atual.

> **Critério de Conclusão**: Nome eleitoral, cargo, partido e UF claramente mapeados para direcionar as fontes de dados corretas.

---

### Passo 2 — Coleta de Dados Oficiais de Transparência

Execute as ferramentas de extração direta conforme o cargo identificado:

1. **Se Deputado Federal**:
   ```bash
   python3 scripts/fetch_camara.py "<Nome do Político>"
   ```
   *Extrai: ID, biografia, gabinete, e-mail institucional, redes sociais, remuneração base, projetos de lei recentes, comissões e frentes parlamentares.*

2. **Se Senador da República**:
   ```bash
   python3 scripts/fetch_senado.py "<Nome do Senador>"
   ```
   *Extrai: Código parlamentar, dados de identificação, mandato, suplentes, bloco, matérias legislativas e canais de transparência de despesas.*

3. **Se Governador, Prefeito, Deputado Estadual ou outros cargos**:
   - Consulte o guia em [sources-guide.md](references/sources-guide.md).
   - Realize buscas direcionadas nos portais de transparência do respectivo órgão/estado para levantar salário bruto oficial e verbas indenizatórias.

4. **Histórico Eleitoral e Bens (TSE DivulgaCandContas)**:
   - Consulte o histórico de declarações de bens no TSE (ano a ano) e o patrimônio declarado mais recente.

> **Critério de Conclusão**: Objeto base de dados contendo perfil biográfico, remuneração oficial, auxílios/cota, assiduidade e lista de proposições ou realizações registrado sem lacunas fundamentais.

---

### Passo 3 — Pesquisa Investigativa e Compilado de Notícias / Escândalos

Execute busca sistemática de notícias, investigações e fatos notórios respeitando as diretrizes de [legal-journalism-ethics.md](references/legal-journalism-ethics.md):

1. **Consultas de Investigação e Processos**:
   - Pesquise operações da Polícia Federal, inquéritos no Ministério Público, processos no STF/STJ/TJs e representações em Conselhos de Ética.
   - Utilize as queries estruturadas (Dorks) descritas em [sources-guide.md](references/sources-guide.md).
2. **Para cada fato ou escândalo relevante identificado**:
   - Defina um **Título Claro e Objetivo**.
   - Registre o **Ano / Data** aproximada do fato.
   - Classifique a **Categoria** (ex: *Operação Policial*, *Investigação MP/STF*, *Uso de Verba Indenizatória*, *Processo Eleitoral*, *Controvérsia Ética*).
   - Defina o **Status Atual**:
     - `Condenado` ou `Denunciado` (Badge Vermelho)
     - `Em Investigação` ou `Em Apuração` (Badge Amarelo)
     - `Arquivado`, `Absolvido` ou `Inocentado` (Badge Verde)
     - `Notícia de Interesse Público` (Badge Azul)
   - Escreva um **Resumo dos Fatos** conciso e neutro baseado em fatos auditáveis.
   - Registre a **Posição da Defesa / Desfecho Judicial** (garantia obrigatória do contraditório).
   - Anexe links para veículos de imprensa reconhecidos (ex: G1, Folha, Estadão, UOL, Poder360, Congresso em Foco).

> **Critério de Conclusão**: Lista com todos os fatos notórios, operações ou controvérsias de repercussão pública documentados com data, resumo, status atual, manifestação da defesa e fontes jornalísticas.

---

### Passo 4 — Consolidação, Geração do Relatório HTML e Atualização do Índice

1. Crie um arquivo JSON temporário com os dados complementares ou monte o payload estruturado de acordo com [dossier-schema.md](references/dossier-schema.md).
2. Execute o gerador `generate_dossier_html.py` ou o orquestrador `run_dossier.py`:
   ```bash
   python3 scripts/generate_dossier_html.py /tmp/politico_full.json
   ```
3. O script gravará o relatório em `~/.dossie-politico/<Nome_Do_Politico>.html` e atualizará automaticamente o arquivo `~/.dossie-politico/index.html` e `~/.dossie-politico/index.json`.

> **Critério de Conclusão**: Arquivo individual gerado e índice geral `~/.dossie-politico/index.html` atualizado com o novo político listado no catálogo.

---

### Passo 5 — Apresentação dos Resultados ao Usuário

Apresente um resumo executivo claro diretamente no chat contendo:
1. Links clicáveis locais:
   - `[Abrir Dossiê Completo](file:///Users/<usuario>/.dossie-politico/<nome>.html)`
   - `[Ver Índice Geral de Análises](file:///Users/<usuario>/.dossie-politico/index.html)`
2. Destaques principais do dossiê:
   - **Identificação**: Cargo, Partido, UF, Mandato.
   - **Remuneração & Gastos**: Salário base oficial e benefícios.
   - **Atuação Parlamentar**: Quantidade de proposições e temas de destaque.
   - **Patrimônio**: Último valor declarado no TSE.
   - **Investigações & Notícias**: Síntese dos principais tópicos com seus respectivos desfechos.

> **Critério de Conclusão**: Resposta concisa no chat com link navegável para o relatório individual e o índice geral.
