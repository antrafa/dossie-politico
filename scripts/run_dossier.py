#!/usr/bin/env python3
"""
run_dossier.py - Orquestrador principal da skill dossie-politico.
Executa a busca em APIs abertas (Câmara/Senado/TSE), compila o JSON do dossiê, gera o HTML e atualiza o índice em ~/.dossie-politico/
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Import dos módulos locais
script_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(script_dir))

from fetch_camara import fetch_deputado_por_nome
from fetch_senado import fetch_senador_por_nome
from fetch_tse_transparency import build_transparency_links
from generate_dossier_html import build_dossier_file

def run_investigation(nome_politico: str, extra_data_file: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
    print(f"[*] Iniciando investigação e auditoria pública para: '{nome_politico}'...")
    
    dossier: Dict[str, Any] = {
        'nome': nome_politico,
        'nome_eleitoral': nome_politico,
        'nome_civil': nome_politico,
        'cargo': 'Agente Público',
        'partido': 'A apurar',
        'uf': 'BR',
        'proposicoes_principais': [],
        'controversias_e_noticias': [],
        'evolucao_patrimonial': [],
        'auxilios_previstos': [],
        'links_transparencia': build_transparency_links(nome_politico)
    }

    # 1. Tentar Câmara dos Deputados
    print("[1/3] Consultando API de Dados Abertos da Câmara dos Deputados...")
    camara_res = fetch_deputado_por_nome(nome_politico)
    if camara_res and camara_res.get('cargo'):
        print(f" [+] Encontrado na Câmara: {camara_res.get('nome_eleitoral')} ({camara_res.get('partido')}-{camara_res.get('uf')})")
        dossier.update(camara_res)
    else:
        # 2. Tentar Senado Federal
        print("[2/3] Consultando API de Dados Abertos do Senado Federal...")
        senado_res = fetch_senador_por_nome(nome_politico)
        if senado_res and senado_res.get('cargo'):
            print(f" [+] Encontrado no Senado: {senado_res.get('nome_eleitoral')} ({senado_res.get('partido')}-{senado_res.get('uf')})")
            dossier.update(senado_res)
        else:
            print("[!] Não localizado nas APIs diretas de parlamentares federais em exercício (pode ser Governador, Prefeito, Deputado Estadual ou ex-mandatário).")

    # 3. Mesclar dados extras (notícias, escândalos, TSE, etc.) se fornecidos
    if extra_data_file and os.path.exists(extra_data_file):
        print(f"[3/3] Mesclando dados adicionais de investigações/notícias de '{extra_data_file}'...")
        with open(extra_data_file, 'r', encoding='utf-8') as f:
            extra = json.load(f)
            for k, v in extra.items():
                if isinstance(v, list) and k in dossier and isinstance(dossier[k], list):
                    dossier[k] = v + dossier[k]
                else:
                    dossier[k] = v

    # 4. Gerar arquivo HTML e atualizar o índice
    output_html_path = build_dossier_file(dossier, output_dir)
    target_folder = os.path.dirname(output_html_path)
    index_path = os.path.join(target_folder, "index.html")
    
    print(f"\n[✓] Dossiê concluído com sucesso!")
    print(f"    Relatório: {output_html_path}")
    print(f"    Índice Geral: {index_path}")
    
    return {
        'status': 'success',
        'html_path': output_html_path,
        'index_path': index_path,
        'dossier_data': dossier
    }

def main():
    parser = argparse.ArgumentParser(description="Gera dossiê de transparência de um político em HTML na pasta ~/.dossie-politico/")
    parser.add_argument('nome', help="Nome do político a ser investigado")
    parser.add_argument('--extra-json', help="Caminho para arquivo JSON com notícias e dados complementares", default=None)
    parser.add_argument('--output-dir', help="Diretório de saída (padrão: ~/.dossie-politico)", default=None)
    parser.add_argument('--json-only', action='store_true', help="Apenas imprime os dados JSON sem gerar HTML")
    
    args = parser.parse_args()
    
    result = run_investigation(args.nome, args.extra_json, args.output_dir)
    if args.json_only:
        print(json.dumps(result['dossier_data'], indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
