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
from generate_dossier_html import build_dossier_file, open_index_file, validate_coverage_record

def run_investigation(
    nome_politico: str,
    extra_data_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    open_index: bool = True,
    render_html: bool = True,
    check_links: bool = True,
    camara_id: Optional[int] = None,
    senado_codigo: Optional[str] = None,
) -> Dict[str, Any]:
    print(f"[*] Iniciando investigação e auditoria pública para: '{nome_politico}'...")

    extra: Dict[str, Any] = {}
    if extra_data_file:
        if not os.path.exists(extra_data_file):
            raise FileNotFoundError(f"Arquivo de dados complementares não encontrado: {extra_data_file}")
        with open(extra_data_file, 'r', encoding='utf-8') as f:
            extra = json.load(f)
    # Falha antes das chamadas de rede: sem cobertura_pesquisa o dossiê seria recusado no fim.
    if render_html:
        validate_coverage_record(extra)
    
    dossier: Dict[str, Any] = {
        'nome': nome_politico,
        'nome_eleitoral': nome_politico,
        'nome_civil': nome_politico,
        'cargo': 'Agente Público',
        'partido': 'A apurar',
        'uf': 'BR',
        'data_corte': 'Não informada',
        'resumo_cidadao_ia': {
            'sintese': 'Síntese cidadã ainda não produzida. Consulte as seções detalhadas e as fontes vinculadas.',
            'pontos_chave': [],
            'lacunas': ['Pesquisa complementar e síntese por IA ainda necessárias.'],
            'aviso': 'Conteúdo preliminar; confira todas as fontes antes de formar sua conclusão.'
        },
        'proposicoes_principais': [],
        'controversias_e_noticias': [],
        'evolucao_patrimonial': [],
        'auxilios_previstos': [],
        'links_transparencia': build_transparency_links(nome_politico)
    }

    # 1. Tentar Câmara dos Deputados
    print("[1/3] Consultando API de Dados Abertos da Câmara dos Deputados...")
    camara_res = fetch_deputado_por_nome(nome_politico, camara_id)
    if camara_res and camara_res.get('cargo'):
        print(f" [+] Encontrado na Câmara: {camara_res.get('nome_eleitoral')} ({camara_res.get('partido')}-{camara_res.get('uf')})")
        dossier.update(camara_res)
    else:
        # 2. Tentar Senado Federal
        print("[2/3] Consultando API de Dados Abertos do Senado Federal...")
        senado_res = fetch_senador_por_nome(nome_politico, senado_codigo)
        if senado_res and senado_res.get('cargo'):
            print(f" [+] Encontrado no Senado: {senado_res.get('nome_eleitoral')} ({senado_res.get('partido')}-{senado_res.get('uf')})")
            dossier.update(senado_res)
        else:
            print("[!] Não localizado nas APIs diretas de parlamentares federais em exercício (pode ser Governador, Prefeito, Deputado Estadual ou ex-mandatário).")

    # 3. Mesclar dados extras (notícias, escândalos, TSE, etc.) se fornecidos
    if extra:
        print(f"[3/3] Mesclando dados adicionais de investigações/notícias de '{extra_data_file}'...")
        for k, v in extra.items():
            if isinstance(v, list) and k in dossier and isinstance(dossier[k], list):
                dossier[k] = v + dossier[k]
            else:
                dossier[k] = v

    if not render_html:
        return {'status': 'success', 'html_path': None, 'index_path': None,
                'index_opened': False, 'dossier_data': dossier}

    # 4. Gerar arquivo HTML e atualizar o índice
    output_html_path = build_dossier_file(dossier, output_dir, check_links=check_links)
    target_folder = os.path.dirname(output_html_path)
    index_path = os.path.join(target_folder, "index.html")
    
    print(f"\n[✓] Dossiê concluído com sucesso!")
    print(f"    Relatório: {output_html_path}")
    print(f"    Índice Geral: {index_path}")
    index_opened = False
    if open_index:
        index_opened = open_index_file(index_path)
        if index_opened:
            print("    Índice aberto no navegador padrão.")
        else:
            print("    [!] O índice foi gerado, mas o navegador não confirmou a abertura automática.")
    
    return {
        'status': 'success',
        'html_path': output_html_path,
        'index_path': index_path,
        'index_opened': index_opened,
        'dossier_data': dossier
    }

def main():
    parser = argparse.ArgumentParser(description="Gera dossiê de transparência de um político em HTML na pasta ~/.dossie-politico/")
    parser.add_argument('nome', help="Nome do político a ser investigado")
    parser.add_argument('--extra-json', help="Caminho para arquivo JSON com notícias e dados complementares", default=None)
    parser.add_argument('--output-dir', help="Diretório de saída (padrão: ~/.dossie-politico)", default=None)
    parser.add_argument('--json-only', action='store_true', help="Apenas imprime os dados JSON: não gera HTML, não toca no índice e não abre o navegador")
    parser.add_argument('--id', dest='camara_id', type=int, default=None, help="ID do deputado na Câmara, quando o nome for ambíguo")
    parser.add_argument('--codigo', dest='senado_codigo', default=None, help="Código do senador, quando o nome for ambíguo")
    parser.add_argument('--no-check-links', action='store_true', help="Não verifica se as URLs das fontes citadas resolvem")
    parser.add_argument('--no-open-index', action='store_true', help="Não abre o índice (somente testes/ambientes sem interface)")
    
    args = parser.parse_args()
    
    try:
        result = run_investigation(
            args.nome,
            args.extra_json,
            args.output_dir,
            open_index=not args.no_open_index,
            render_html=not args.json_only,
            check_links=not args.no_check_links,
            camara_id=args.camara_id,
            senado_codigo=args.senado_codigo,
        )
    except LookupError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1
    if args.json_only:
        print(json.dumps(result['dossier_data'], indent=2, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
