# Estrutura e Esquema de Dados do Dossiê (JSON Schema)

O dossiê político compilado segue a seguinte estrutura padronizada de dados antes da renderização em HTML:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DossiePoliticoData",
  "type": "object",
  "required": [
    "nome_eleitoral",
    "cargo",
    "partido",
    "uf"
  ],
  "properties": {
    "nome_eleitoral": { "type": "string" },
    "nome_civil": { "type": "string" },
    "cargo": { "type": "string", "example": "Deputado Federal, Senador da República, Governador, etc." },
    "partido": { "type": "string", "example": "PP, PL, PT, PSD, etc." },
    "uf": { "type": "string", "example": "SP, RJ, MG, etc." },
    "situacao": { "type": "string", "example": "Exercício, Licenciado, Afastado" },
    "foto_url": { "type": "string" },
    "email": { "type": "string" },
    "telefone_gabinete": { "type": "string" },
    "data_nascimento": { "type": "string" },
    "municipio_nascimento": { "type": "string" },
    "escolaridade": { "type": "string" },
    "redes_sociais": {
      "type": "array",
      "items": { "type": "string" }
    },
    "salario_oficial_base": { "type": "string", "example": "R$ 44.008,52" },
    "auxilios_previstos": {
      "type": "array",
      "items": { "type": "string" }
    },
    "assiduidade_percentual": { "type": "string", "example": "94.5% de presença nas sessões deliberativas" },
    "proposicoes_principais": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "tipo": { "type": "string", "example": "PL, PEC, MPV" },
          "numero": { "type": ["string", "number"] },
          "ano": { "type": ["string", "number"] },
          "ementa": { "type": "string" },
          "data": { "type": "string" },
          "link": { "type": "string" }
        }
      }
    },
    "evolucao_patrimonial": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "ano": { "type": ["string", "number"] },
          "cargo_disputado": { "type": "string" },
          "valor": { "type": "number" },
          "valor_formatado": { "type": "string" }
        }
      }
    },
    "controversias_e_noticias": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "titulo": { "type": "string" },
          "data": { "type": "string" },
          "categoria": { "type": "string", "example": "Operação Policial, Investigação STF, Uso de Cota, Processo Eleitoral" },
          "status": { "type": "string", "example": "Em Investigação, Denunciado, Réu, Condenado, Absolvido, Arquivado" },
          "resumo": { "type": "string" },
          "posicao_defesa": { "type": "string" },
          "fontes": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "veiculo": { "type": "string" },
                "url": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "link_perfil_oficial": { "type": "string" },
    "link_transparencia_gastos": { "type": "string" },
    "link_tse": { "type": "string" }
  }
}
```
