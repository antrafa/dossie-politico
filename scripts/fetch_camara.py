#!/usr/bin/env python3
"""
fetch_camara.py - Consulta e estruturação de dados da API da Câmara dos Deputados.
Fonte oficial: https://dadosabertos.camara.leg.br/api/v2/
"""

import sys
import json
import urllib.request
import urllib.parse
import unicodedata
from typing import Dict, Any, Optional, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PoliticoDossie/1.0',
    'Accept': 'application/json'
}

def normalize(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

def http_get(url: str, timeout: int = 15) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        sys.stderr.write(f"[WARN] Falha ao consultar {url}: {e}\n")
    return None

def fetch_deputado_por_nome(nome: str) -> Optional[Dict[str, Any]]:
    norm_query = normalize(nome)
    query_encoded = urllib.parse.quote(nome.strip())
    url_search = f"https://dadosabertos.camara.leg.br/api/v2/deputados?nome={query_encoded}&ordem=ASC&ordenarPor=nome"
    
    data = http_get(url_search)
    if not data or not data.get('dados'):
        url_all = "https://dadosabertos.camara.leg.br/api/v2/deputados?ordem=ASC&ordenarPor=nome&itens=600"
        data_all = http_get(url_all)
        if not data_all or not data_all.get('dados'):
            return None
        candidates = [
            d for d in data_all['dados']
            if norm_query in normalize(d['nome']) or all(part in normalize(d['nome']) for part in norm_query.split())
        ]
        if not candidates:
            return None
        dep_summary = candidates[0]
    else:
        dep_summary = data['dados'][0]

    dep_id = dep_summary['id']
    
    # Detalhes completos
    det_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}")
    det = det_data.get('dados', {}) if det_data else {}
    
    # Proposições de autoria recente
    props_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/proposicoes?idDeputadoAutor={dep_id}&ordem=DESC&ordenarPor=ano&itens=25")
    props = props_data.get('dados', []) if props_data else []
    
    # Frentes parlamentares
    frentes_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/frentes")
    frentes = frentes_data.get('dados', []) if frentes_data else []
    
    # Órgãos / Comissões
    orgaos_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/orgaos")
    orgaos = orgaos_data.get('dados', []) if orgaos_data else []
    
    # Discursos recentes
    discursos_data = http_get(f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/discursos?ordenarPor=dataHoraInicio&ordem=DESC&itens=10")
    discursos = discursos_data.get('dados', []) if discursos_data else []

    ultimo_status = det.get('ultimoStatus', {})
    gabinete = ultimo_status.get('gabinete', {})

    return {
        'fonte': 'Câmara dos Deputados (API Dados Abertos)',
        'id_origem': dep_id,
        'cargo': 'Deputado(a) Federal',
        'nome_eleitoral': ultimo_status.get('nomeEleitoral', dep_summary.get('nome')),
        'nome_civil': det.get('nomeCivil', dep_summary.get('nome')),
        'partido': ultimo_status.get('siglaPartido', dep_summary.get('siglaPartido')),
        'uf': ultimo_status.get('siglaUf', dep_summary.get('siglaUf')),
        'legislatura': ultimo_status.get('idLegislatura', 57),
        'situacao': ultimo_status.get('situacao', 'Exercício'),
        'condicao_eleitoral': ultimo_status.get('condicaoEleitoral', 'Titular'),
        'foto_url': ultimo_status.get('urlFoto', dep_summary.get('urlFoto')),
        'email': gabinete.get('email') or ultimo_status.get('email'),
        'telefone_gabinete': gabinete.get('telefone'),
        'sala_gabinete': f"Gabinete {gabinete.get('nome')}, Prédio {gabinete.get('predio')}, Sala {gabinete.get('sala')}, Andar {gabinete.get('andar')}" if gabinete else None,
        'data_nascimento': det.get('dataNascimento'),
        'municipio_nascimento': f"{det.get('municipioNascimento', '')} - {det.get('ufNascimento', '')}".strip(" -"),
        'escolaridade': det.get('escolaridade'),
        'redes_sociais': det.get('redeSocial', []),
        'salario_oficial_base': 'R$ 44.008,52 (Subsidio Deputado Federal - Decreto Legislativo 172/2022)',
        'auxilios_previstos': [
            'Cota para o Exercício da Atividade Parlamentar (CEAP - R$ 30.788,66 a R$ 45.612,53 conforme UF)',
            'Verba de Gabinete (R$ 118.823,24/mês para até 25 secretários)',
            'Auxílio-moradia (R$ 4.253,00) ou Apartamento Funcional em Brasília',
            'Ajuda de custo no início e fim do mandato (R$ 44.008,52)'
        ],
        'proposicoes_principais': [
            {
                'id': p.get('id'),
                'tipo': p.get('siglaTipo'),
                'numero': p.get('numero'),
                'ano': p.get('ano'),
                'ementa': p.get('ementa'),
                'data': p.get('dataApresentacao', '')[:10],
                'link': f"https://www.camara.leg.br/proposicoesWeb/fichadetramitacao?idProposicao={p.get('id')}"
            } for p in props
        ],
        'frentes_parlamentares_count': len(frentes),
        'frentes_destaque': [f.get('titulo') for f in frentes[:8]],
        'comissoes_orgaos': [
            {
                'nome': o.get('nomeOrgao'),
                'sigla': o.get('siglaOrgao'),
                'cargo': o.get('titulo', 'Membro'),
                'data_inicio': o.get('dataInicio')
            } for o in orgaos[:10]
        ],
        'discursos_recentes': [
            {
                'data_hora': d.get('dataHoraInicio'),
                'fase': d.get('faseEvento'),
                'sumario': d.get('sumario')
            } for d in discursos
        ],
        'link_perfil_oficial': f"https://www.camara.leg.br/deputados/{dep_id}",
        'link_transparencia_gastos': f"https://www.camara.leg.br/deputados/{dep_id}/gastos",
        'link_presenca': f"https://www.camara.leg.br/deputados/{dep_id}/presenca-plenario"
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Informe o nome do deputado: python3 fetch_camara.py "<Nome>"'}))
        sys.exit(1)
    
    nome_arg = " ".join(sys.argv[1:])
    resultado = fetch_deputado_por_nome(nome_arg)
    if resultado:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({'status': 'not_found', 'message': f'Deputado não encontrado na API da Câmara para: {nome_arg}'}))
