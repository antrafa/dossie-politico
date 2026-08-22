# Guia de Fontes e Portais de Transparência Pública (Brasil)

Este documento reúne os principais endpoints de APIs oficiais, portais de dados abertos e estratégias de busca (Google Dorking) para auditoria e compilação de dossiês de agentes públicos no Brasil.

---

## 1. Poder Legislativo Federal

### Câmara dos Deputados (Deputados Federais)
- **Portal de Dados Abertos (API REST v2)**: `https://dadosabertos.camara.leg.br/api/v2`
- **Documentação Swagger**: `https://dadosabertos.camara.leg.br/swagger/api.html`
- **Principais Endpoints**:
  - `GET /deputados?nome={nome}`: Busca deputado por nome.
  - `GET /deputados/{id}`: Detalhes biográficos, partido, UF, gabinete, e-mail institucional e redes sociais.
  - `GET /deputados/{id}/despesas?ano={ano}`: Gastos da Cota para o Exercício da Atividade Parlamentar (CEAP).
  - `GET /deputados/{id}/discursos`: Histórico de discursos em plenário.
  - `GET /deputados/{id}/frentes`: Frentes parlamentares das quais participa.
  - `GET /deputados/{id}/orgaos`: Comissões e mesas das quais é titular ou suplente.
  - `GET /proposicoes?idDeputadoAutor={id}&ordem=DESC&ordenarPor=ano`: Projetos de Lei (PL), PECs, requerimentos de autoria.
- **Página Web Oficial do Parlamentar**: `https://www.camara.leg.br/deputados/{id}`
- **Presença em Plenário e Comissões**: `https://www.camara.leg.br/deputados/{id}/presenca-plenario`

### Senado Federal (Senadores da República)
- **API de Dados Abertos (REST JSON/XML)**: `https://legis.senado.leg.br/dadosabertos/`
- **Principais Endpoints**:
  - `GET /senador/lista/atual.json`: Lista completa de senadores em exercício com dados de identificação e mandato.
  - `GET /senador/{codigo}.json`: Detalhes cadastrais, telefones, bloco parlamentar e suplentes.
  - `GET /senador/{codigo}/autorias.json`: Propostas legislativas e relatorias do senador.
  - `GET /senador/{codigo}/votacoes.json`: Histórico de votações nominais.
- **Portal de Transparência do Senado (CEAPS)**: `https://www.senado.leg.br/transparencia/sen/{codigo}/`
- **Página de Perfil do Senador**: `https://www25.senado.leg.br/web/senadores/senador/-/perfil/{codigo}`

---

## 2. Justiça Eleitoral e Patrimônio (TSE)

### TSE DivulgaCandContas
- **Portal Oficial**: `https://divulgacandcontas.tse.jus.br/`
- **Informações Disponibilizadas**:
  - Registro de candidatura e coligações históricas
  - **Declaração de Bens e Evolução Patrimonial** (imóveis, empresas, contas, aplicações)
  - Prestação de contas eleitorais (doadores, receitas de campanha, despesas com fornecedores)
  - Proposta de governo registrada (para cargos executivos: Presidente, Governador, Prefeito)
- **API REST (DivulgaCandContas)**:
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/eleicao/eleicoes`
  - `GET https://divulgacandcontas.tse.jus.br/divulga/rest/v1/candidatura/buscar/{ano}/{idEleicao}/candidatos`

---

## 3. Poder Executivo e Governo Federal (CGU / Portal da Transparência)

- **Portal da Transparência do Governo Federal**: `https://portaldatransparencia.gov.br/`
- **API do Portal da Transparência**: `https://api.portaldatransparencia.gov.br/` (Requer chave de API ou scraping/consulta web)
- **Informações Auditáveis**:
  - Remuneração de servidores públicos, ministros e secretários nacionais
  - Registro de Sanções:
    - **CEIS** (Cadastro de Empresas Inidôneas e Suspensas)
    - **CNEP** (Cadastro Nacional de Empresas Punidas)
    - **CEPIM** (Cadastro de Entidades Privadas Sem Fins Lucrativos Impedidas)
    - **CEAF** (Cadastro de Expulsões da Administração Federal)
  - Cartão de Pagamento do Governo Federal (CPGF) e diárias de viagem

---

## 4. Órgãos de Controle e Tribunais Superiores

- **TCU (Tribunal de Contas da União)**:
  - `https://pesquisa.apps.tcu.gov.br/`
  - Consulta de contas julgadas irregulares, inabilitação para função pública e relatórios de auditoria.
- **STF (Supremo Tribunal Federal)**:
  - `https://portal.stf.jus.br/processos/`
  - Inquéritos policiais (INQ), Ações Penais (AP), Reclamações (Rcl) e Ações Diretas de Inconstitucionalidade (ADI).
- **STJ (Superior Tribunal de Justiça)**:
  - `https://processo.stj.jus.br/processo/pesquisa/`
  - Ações contra governadores e desembargadores (foro por prerrogativa de função).

---

## 5. Poderes Estaduais e Municipais

Para **Governadores, Prefeitos, Deputados Estaduais e Vereadores**:

### Assembleias Legislativas (ALEs)
- Exemplos: `ALESP` (SP), `ALERJ` (RJ), `ALMG` (MG), `ALEPE` (PE), `ALRS` (RS).
- Cada ALE mantém seu próprio Portal da Transparência com salários, verbas indenizatórias de gabinete e diárias.

### Câmaras Municipais e Prefeituras
- Consultar o Portal da Transparência do município (`transparencia.<municipio>.<uf>.gov.br` ou `camara<municipio>.<uf>.leg.br`).

---

## 6. Estratégias de Busca Jornalística e Investigativa (Dorks)

Para levantar escândalos, notícias, investigações da Polícia Federal e do Ministério Público com rigor e neutralidade, utilize queries estruturadas:

```text
# Investigações e Operações Policiais
"<Nome do Político>" AND ("operação" OR "Polícia Federal" OR "Ministério Público" OR "busca e apreensão" OR "inquérito")

# Processos Judiciais e Tribunais
"<Nome do Político>" AND ("STF" OR "STJ" OR "Ação Penal" OR "denúncia" OR "réu" OR "Tribunal de Contas")

# Gastos, Salário e Verbas
"<Nome do Político>" AND ("cota parlamentar" OR "verba indenizatória" OR "super-salário" OR "gastos de gabinete" OR "nepotismo")

# Patrimônio e TSE
"<Nome do Político>" AND ("declaração de bens" OR "patrimônio" OR "TSE" OR "DivulgaCandContas")

# Desfechos e Decisões Judiciais (Garantia do contraditório)
"<Nome do Político>" AND ("arquivado" OR "absolvido" OR "defesa alega" OR "inocentado" OR "prescrito" OR "rejeitada a denúncia")
```
