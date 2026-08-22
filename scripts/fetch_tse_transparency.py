#!/usr/bin/env python3
"""
fetch_tse_transparency.py - Consulta e suporte à extração de dados eleitorais e patrimônio do TSE (DivulgaCandContas)
Fonte oficial: https://divulgacandcontas.tse.jus.br/
"""

import sys
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PoliticoDossie/1.0',
    'Accept': 'application/json'
}

def get_tse_endpoints(ano: int, uf: str) -> Dict[str, str]:
    """Retorna URLs padrão do DivulgaCandContas por ano de eleição."""
    base = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"
    return {
        'eleicao_consulta': f"{base}/eleicao/eleicoes",
        'candidaturas': f"{base}/candidatura/listar/{ano}/{uf}/2030402022/candidatos",
        'portal_busca': f"https://divulgacandcontas.tse.jus.br/#/candidato/{ano}"
    }

def build_transparency_links(nome: str, cargo: str = "", uf: str = "") -> Dict[str, Any]:
    nome_encoded = urllib.parse.quote(nome)
    
    return {
        'tse_divulgacand': f"https://divulgacandcontas.tse.jus.br/#/consulta/candidatos",
        'tse_busca_geral': f"https://divulgacandcontas.tse.jus.br/#/busca/{nome_encoded}",
        'portal_transparencia_federal': f"https://portaldatransparencia.gov.br/busca?termo={nome_encoded}",
        'portal_transparencia_servidores': f"https://portaldatransparencia.gov.br/servidores/busca?termo={nome_encoded}",
        'tcu_jurisprudencia_e_inabilitados': f"https://pesquisa.apps.tcu.gov.br/#/pesquisa/jurisprudencia?termo={nome_encoded}",
        'cgu_ceis_sancoes': f"https://portaldatransparencia.gov.br/sancoes/ceis?termo={nome_encoded}",
        'jusbrasil_processos': f"https://www.jusbrasil.com.br/jurisprudencia/busca?q={nome_encoded}",
        'stf_processos': f"https://portal.stf.jus.br/processos/listarProcessos.asp?termo={nome_encoded}",
        'stj_processos': f"https://processo.stj.jus.br/processo/pesquisa/?termo={nome_encoded}"
    }

if __name__ == '__main__':
    nome = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Arthur Lira"
    links = build_transparency_links(nome)
    print(json.dumps({'politico': nome, 'links_transparencia': links}, indent=2, ensure_ascii=False))
