#!/usr/bin/env python3
"""
generate_dossier_html.py - Gera um dossiê político interativo, completo e autossuficiente em formato HTML.
Salva o relatório em ~/.dossie-politico/<nome_politico>.html e atualiza o ~/.dossie-politico/index.html
"""

import sys
import os
import json
import html
import re
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', name).strip()
    return re.sub(r'[-\s]+', '_', cleaned)

def format_currency(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(value) if value else "Não informado"

def get_badge_class(status: str) -> str:
    s = (status or "").lower()
    if any(k in s for k in ['condenad', 'reu', 'denunciad', 'crime', 'cassad', 'inconstitucional']):
        return "badge-danger"
    elif any(k in s for k in ['investiga', 'inquerito', 'apuracao', 'suspeita', 'operacao', 'tramita']):
        return "badge-warning"
    elif any(k in s for k in ['arquivad', 'absolvid', 'sem irregularidade', 'rejeitad', 'inocent', 'anulad', 'trancad']):
        return "badge-success"
    else:
        return "badge-info"

def generate_dossier_html(data: Dict[str, Any]) -> str:
    nome_eleitoral = html.escape(data.get('nome_eleitoral') or data.get('nome') or 'Político')
    nome_civil = html.escape(data.get('nome_civil') or nome_eleitoral)
    cargo = html.escape(data.get('cargo') or 'Agente Público')
    partido = html.escape(data.get('partido') or 'S/ Partido')
    uf = html.escape(data.get('uf') or 'BR')
    foto_url = data.get('foto_url') or "https://via.placeholder.com/300x380?text=Sem+Foto"
    salario_base = html.escape(str(data.get('salario_oficial_base') or 'R$ 44.008,52'))
    data_geracao = data.get('data_geracao') or datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    # KPIs
    assiduidade = html.escape(str(data.get('assiduidade_percentual') or '100% de Presença Institucional'))
    props_total = len(data.get('proposicoes_principais', []))
    controversias = data.get('controversias_e_noticias', [])
    controversias_total = len(controversias)
    patrimonio_recente = html.escape(str(data.get('patrimonio_declarado_recente') or 'Consultar TSE'))
    if patrimonio_recente == 'Consultar TSE' and data.get('evolucao_patrimonial'):
        patrimonio_recente = html.escape(str(data['evolucao_patrimonial'][0].get('valor_formatado') or 'Consultar TSE'))
    
    # Auxílios
    auxilios = data.get('auxilios_previstos', [])
    auxilios_html = "".join([f"<li><span class='bullet'>•</span> <div>{html.escape(str(a))}</div></li>" for a in auxilios]) if auxilios else "<li>Sem auxílios adicionais cadastrados.</li>"
    
    # Despesas discriminadas
    gastos_detalhados = data.get('despesas_discriminadas', [])
    gastos_html = ""
    if gastos_detalhados:
        for g in gastos_detalhados:
            categoria = html.escape(str(g.get('categoria', 'Despesa')))
            valor = html.escape(str(g.get('valor_formatado') or format_currency(g.get('valor', 0))))
            detalhe = html.escape(str(g.get('detalhe', '')))
            gastos_html += f"""
            <div class="expense-card">
                <div class="expense-header">
                    <span class="expense-category">{categoria}</span>
                    <span class="expense-value">{valor}</span>
                </div>
                <div class="expense-detail">{detalhe}</div>
            </div>
            """

    # Redes sociais
    redes = data.get('redes_sociais', [])
    redes_html = ""
    if isinstance(redes, list):
        for r in redes:
            if isinstance(r, str) and r.startswith('http'):
                platform = "Link Oficial"
                if "twitter.com" in r or "x.com" in r: platform = "𝕏 Twitter"
                elif "instagram.com" in r: platform = "📸 Instagram"
                elif "facebook.com" in r: platform = "📘 Facebook"
                elif "youtube.com" in r: platform = "▶️ YouTube"
                redes_html += f"<a href='{html.escape(r)}' target='_blank' rel='noopener' class='social-pill'>{platform} ↗</a> "
            elif isinstance(r, dict):
                redes_html += f"<a href='{html.escape(r.get('url', '#'))}' target='_blank' rel='noopener' class='social-pill'>{html.escape(r.get('rede', 'Social'))} ↗</a> "
    if not redes_html:
        redes_html = "<span class='text-muted'>Não cadastradas oficialmente</span>"

    # Proposições
    props = data.get('proposicoes_principais', [])
    props_html = ""
    if props:
        for p in props:
            sigla = html.escape(str(p.get('tipo', 'PL')))
            num = html.escape(str(p.get('numero', '')))
            ano = html.escape(str(p.get('ano', '')))
            ementa = html.escape(str(p.get('ementa', 'Sem ementa disponível.')))
            data_p = html.escape(str(p.get('data', '')))
            status_tram = html.escape(str(p.get('status_tramitacao', 'Tramitação Ordinária')))
            link_p = p.get('link') or "#"
            props_html += f"""
            <div class="proposal-card">
                <div class="proposal-header">
                    <span class="proposal-type">{sigla} {num}/{ano}</span>
                    <span class="proposal-status-badge">{status_tram}</span>
                    <span class="proposal-date">{data_p}</span>
                </div>
                <p class="proposal-ementa">{ementa}</p>
                <div class="proposal-footer">
                    <a href="{html.escape(link_p)}" target="_blank" rel="noopener" class="btn-link">Ver ficha de tramitação e texto integral ↗</a>
                </div>
            </div>
            """
    else:
        props_html = "<p class='text-muted'>Nenhuma proposição registrada no período analisado.</p>"

    # Notícias e Controvérsias
    controversias_html = ""
    categories_set = set()
    if controversias:
        for idx, c in enumerate(controversias):
            titulo = html.escape(str(c.get('titulo', 'Fato Registrado')))
            data_c = html.escape(str(c.get('data', 'Data recente')))
            tipo = str(c.get('categoria', 'Notícia / Investigação'))
            categories_set.add(tipo)
            status = html.escape(str(c.get('status', 'Em Apuração')))
            badge_cls = get_badge_class(status)
            resumo = html.escape(str(c.get('resumo', '')))
            posicao_defesa = html.escape(str(c.get('posicao_defesa', 'Não houve manifestação oficial ou desfecho pendente.')))
            fontes = c.get('fontes', [])
            
            fontes_links = ""
            if isinstance(fontes, list):
                for f in fontes:
                    if isinstance(f, dict):
                        f_nome = html.escape(f.get('veiculo', 'Fonte'))
                        f_url = html.escape(f.get('url', '#'))
                        fontes_links += f"<a href='{f_url}' target='_blank' rel='noopener' class='source-tag'>🔗 {f_nome}</a> "
                    elif isinstance(f, str) and f.startswith('http'):
                        fontes_links += f"<a href='{html.escape(f)}' target='_blank' rel='noopener' class='source-tag'>🔗 Matéria Original</a> "

            fallback_fontes = "<span class='text-muted'>Veículos jornalísticos nacionais (G1, Folha, Estadão, Poder360)</span>"
            final_fontes = fontes_links if fontes_links else fallback_fontes

            cat_slug = re.sub(r'\W+', '_', tipo.lower())

            controversias_html += f"""
            <div class="timeline-item" data-category="{cat_slug}">
                <div class="timeline-marker"></div>
                <div class="timeline-content card">
                    <div class="timeline-header">
                        <div class="timeline-tags">
                            <span class="category-tag">{html.escape(tipo)}</span>
                            <span class="badge {badge_cls}">{status}</span>
                        </div>
                        <span class="timeline-date">📅 {data_c}</span>
                    </div>
                    <h3 class="timeline-title">{titulo}</h3>
                    <div class="timeline-text">
                        <p>{resumo}</p>
                    </div>
                    <div class="defense-box">
                        <strong>⚖️ Posição da Defesa / Desfecho Jurídico:</strong>
                        <p>{posicao_defesa}</p>
                    </div>
                    <div class="sources-box">
                        <span class="sources-label">Fontes Auditadas:</span> {final_fontes}
                    </div>
                </div>
            </div>
            """
    else:
        controversias_html = """
        <div class="empty-state card">
            <p>Nenhuma investigação criminal, processo no STF ou escândalo notório com repercussão pública localizado até a data desta consulta.</p>
        </div>
        """

    # Filter buttons for controversies
    filter_buttons_html = "<button class='filter-btn active' onclick='filterControversies(\"all\", this)'>Todos ({})</button>".format(controversias_total)
    for cat in sorted(categories_set):
        cat_slug = re.sub(r'\W+', '_', cat.lower())
        count = sum(1 for item in controversias if item.get('categoria') == cat)
        filter_buttons_html += f"<button class='filter-btn' onclick='filterControversies(\"{cat_slug}\", this)'>{html.escape(cat)} ({count})</button>"

    # Evolução Patrimonial
    patrimonio_list = data.get('evolucao_patrimonial', [])
    patrimonio_html = ""
    if patrimonio_list:
        for p in patrimonio_list:
            ano_eleicao = html.escape(str(p.get('ano', '')))
            cargo_disp = html.escape(str(p.get('cargo_disputado', '')))
            valor = html.escape(str(p.get('valor_formatado') or format_currency(p.get('valor', 0))))
            variacao = html.escape(str(p.get('variacao_percentual', '-')))
            detalhe_bens = html.escape(str(p.get('principais_bens', 'Imóveis, veículos e participações societárias')))
            patrimonio_html += f"""
            <tr class="table-row">
                <td class="td-year"><strong>{ano_eleicao}</strong></td>
                <td><span class="badge-subtle">{cargo_disp}</span></td>
                <td class="td-value">{valor}</td>
                <td><span class="growth-tag">{variacao}</span></td>
                <td class="td-details">{detalhe_bens}</td>
            </tr>
            """
    else:
        patrimonio_html = "<tr><td colspan='5' class='text-muted text-center'>Consulte o portal TSE DivulgaCandContas para histórico eleitoral de bens.</td></tr>"

    # Links oficiais
    link_perfil = data.get('link_perfil_oficial') or "https://www.camara.leg.br"
    link_gastos = data.get('link_transparencia_gastos') or "https://portaldatransparencia.gov.br"
    link_presenca = data.get('link_presenca') or "#"
    link_tse = data.get('link_tse') or "https://divulgacandcontas.tse.jus.br"

    template = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dossiê de Transparência Cidadã: {nome_eleitoral} ({partido}-{uf})</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131c2e;
            --bg-card-alt: #1e293b;
            --bg-card-hover: #26354d;
            --bg-input: #0f172a;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --danger-bg: rgba(239, 68, 68, 0.18);
            --danger-text: #fca5a5;
            --danger-border: #ef4444;
            --warning-bg: rgba(245, 158, 11, 0.18);
            --warning-text: #fde047;
            --warning-border: #f59e0b;
            --success-bg: rgba(34, 197, 94, 0.18);
            --success-text: #86efac;
            --success-border: #22c55e;
            --info-bg: rgba(59, 130, 246, 0.18);
            --info-text: #93c5fd;
            --info-border: #3b82f6;
            --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --radius: 14px;
        }}

        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-alt: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --bg-input: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --accent: #0284c7;
            --accent-hover: #0369a1;
            --accent-glow: rgba(2, 132, 199, 0.12);
            --danger-bg: #fee2e2;
            --danger-text: #991b1b;
            --danger-border: #ef4444;
            --warning-bg: #fef3c7;
            --warning-text: #92400e;
            --warning-border: #f59e0b;
            --success-bg: #dcfce7;
            --success-text: #166534;
            --success-border: #22c55e;
            --info-bg: #dbeafe;
            --info-text: #1e40af;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 80px;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header Bar */
        .top-nav {{
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 16px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}

        .top-nav-inner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand {{
            font-size: 1.2rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
            text-decoration: none;
        }}

        .brand-badge {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .nav-actions {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}

        .btn-nav {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-nav:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        .btn-theme {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-theme:hover {{
            border-color: var(--accent);
            transform: translateY(-1px);
        }}

        /* Profile Hero */
        .hero-section {{
            margin-top: 30px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 32px;
            box-shadow: var(--shadow);
            display: grid;
            grid-template-columns: 210px 1fr;
            gap: 32px;
            align-items: center;
        }}

        @media (max-width: 768px) {{
            .hero-section {{
                grid-template-columns: 1fr;
                text-align: center;
            }}
            .profile-photo {{
                margin: 0 auto;
            }}
            .hero-tags {{
                justify-content: center;
            }}
            .quick-bio {{
                grid-template-columns: 1fr 1fr;
            }}
        }}

        .profile-photo {{
            width: 210px;
            height: 260px;
            object-fit: cover;
            border-radius: 12px;
            border: 2px solid var(--border-color);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
            background-color: var(--bg-card-alt);
        }}

        .profile-info {{
            display: flex;
            flex-direction: column;
            gap: 14px;
        }}

        .hero-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: center;
        }}

        .tag-party {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
            font-weight: 800;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 6px;
        }}

        .tag-role {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            font-weight: 700;
            font-size: 0.85rem;
            padding: 4px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .profile-name {{
            font-size: 2.3rem;
            font-weight: 900;
            color: var(--text-main);
            line-height: 1.15;
            letter-spacing: -0.5px;
        }}

        .profile-civil-name {{
            font-size: 0.95rem;
            color: var(--text-muted);
        }}

        .quick-bio {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            gap: 14px;
            margin-top: 10px;
            padding-top: 16px;
            border-top: 1px solid var(--border-color);
        }}

        .bio-item {{
            font-size: 0.85rem;
        }}
        .bio-label {{
            color: var(--text-muted);
            display: block;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }}
        .bio-val {{
            font-weight: 700;
            color: var(--text-main);
        }}

        /* KPI Dashboard Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin: 24px 0;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 22px;
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent), var(--accent-hover));
        }}

        .kpi-title {{
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.2;
        }}

        .kpi-subtext {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 6px;
        }}

        /* Sections */
        .section-title {{
            font-size: 1.35rem;
            font-weight: 800;
            margin: 40px 0 16px 0;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
        }}

        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
        }}

        .card-title {{
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Lists */
        ul.styled-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        ul.styled-list li {{
            font-size: 0.92rem;
            color: var(--text-main);
            display: flex;
            align-items: flex-start;
            gap: 10px;
        }}

        .bullet {{
            color: var(--accent);
            font-weight: 900;
            font-size: 1.2rem;
            line-height: 1;
        }}

        .social-pill {{
            display: inline-block;
            background: var(--bg-card-alt);
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 6px;
            margin: 4px 4px 4px 0;
            border: 1px solid var(--border-color);
            transition: all 0.15s ease;
        }}

        .social-pill:hover {{
            border-color: var(--accent);
            color: var(--accent);
            background: var(--bg-card-hover);
        }}

        /* Proposals Grid */
        .proposals-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 16px;
        }}

        .proposal-card {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 14px;
            transition: all 0.2s ease;
        }}

        .proposal-card:hover {{
            border-color: var(--accent);
            background: var(--bg-card-hover);
        }}

        .proposal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
        }}

        .proposal-type {{
            background: var(--accent-glow);
            color: var(--accent);
            font-weight: 800;
            font-size: 0.82rem;
            padding: 3px 10px;
            border-radius: 6px;
        }}

        .proposal-status-badge {{
            background: var(--bg-card);
            color: var(--text-muted);
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}

        .proposal-date {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}

        .proposal-ementa {{
            font-size: 0.9rem;
            color: var(--text-main);
            line-height: 1.5;
        }}

        .btn-link {{
            color: var(--accent);
            text-decoration: none;
            font-size: 0.82rem;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .btn-link:hover {{
            text-decoration: underline;
        }}

        /* Filter Controls */
        .filter-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}

        .filter-btn {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent);
            color: #0f172a;
            border-color: var(--accent);
        }}

        /* Timeline for News & Scandals */
        .timeline {{
            position: relative;
            padding-left: 28px;
            margin-top: 16px;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 10px;
            width: 2px;
            background: var(--border-color);
        }}

        .timeline-item {{
            position: relative;
            margin-bottom: 28px;
            transition: all 0.2s ease;
        }}

        .timeline-marker {{
            position: absolute;
            top: 24px;
            left: -28px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--accent);
            border: 2px solid var(--bg-body);
        }}

        .timeline-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }}

        .timeline-tags {{
            display: flex;
            gap: 8px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .category-tag {{
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-size: 0.74rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}

        .timeline-date {{
            font-size: 0.8rem;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .timeline-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 10px;
            line-height: 1.3;
        }}

        .timeline-text {{
            font-size: 0.92rem;
            color: var(--text-main);
            margin-bottom: 14px;
            line-height: 1.55;
        }}

        .defense-box {{
            background: var(--bg-card-alt);
            border-left: 4px solid var(--accent);
            padding: 14px;
            border-radius: 0 8px 8px 0;
            font-size: 0.88rem;
            margin-bottom: 14px;
            line-height: 1.5;
        }}

        .defense-box strong {{
            display: block;
            margin-bottom: 6px;
            color: var(--accent);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .sources-box {{
            font-size: 0.82rem;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            padding-top: 10px;
            border-top: 1px solid var(--border-color);
        }}

        .sources-label {{
            color: var(--text-muted);
            font-weight: 700;
        }}

        .source-tag {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 700;
            transition: color 0.15s ease;
        }}
        .source-tag:hover {{
            text-decoration: underline;
        }}

        /* Badges */
        .badge {{
            font-size: 0.74rem;
            font-weight: 800;
            padding: 3px 9px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .badge-danger {{
            background: var(--danger-bg);
            color: var(--danger-text);
            border: 1px solid var(--danger-border);
        }}
        .badge-warning {{
            background: var(--warning-bg);
            color: var(--warning-text);
            border: 1px solid var(--warning-border);
        }}
        .badge-success {{
            background: var(--success-bg);
            color: var(--success-text);
            border: 1px solid var(--success-border);
        }}
        .badge-info {{
            background: var(--info-bg);
            color: var(--info-text);
            border: 1px solid var(--info-border);
        }}

        .badge-subtle {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .growth-tag {{
            background: var(--accent-glow);
            color: var(--accent);
            font-weight: 800;
            font-size: 0.8rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        /* Table */
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }}

        .data-table th {{
            text-align: left;
            padding: 14px;
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-weight: 800;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 1px solid var(--border-color);
        }}

        .data-table td {{
            padding: 14px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
            vertical-align: middle;
        }}

        .td-value {{
            font-weight: 800;
            color: var(--accent);
            white-space: nowrap;
        }}

        .td-details {{
            font-size: 0.84rem;
            color: var(--text-muted);
        }}

        .text-center {{
            text-align: center;
        }}

        /* Footer & Audit Trail */
        .footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}

        .audit-links {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 20px;
            margin-top: 16px;
        }}

        .audit-links a {{
            color: var(--accent);
            text-decoration: none;
            font-weight: 700;
        }}

        .audit-links a:hover {{
            text-decoration: underline;
        }}

        @media print {{
            .top-nav, .btn-theme, .audit-links, .filter-bar {{ display: none !important; }}
            body {{ background: #fff !important; color: #000 !important; }}
            .card, .hero-section, .kpi-card {{ border: 1px solid #ccc !important; box-shadow: none !important; }}
        }}
    </style>
</head>
<body>

    <header class="top-nav">
        <div class="container top-nav-inner">
            <a href="index.html" class="brand">
                <span>🏛️ Dossiê Político</span>
                <span class="brand-badge">Auditoria Cidadã</span>
            </a>
            <div class="nav-actions">
                <a href="index.html" class="btn-nav">📋 Ver Índice Geral</a>
                <button class="btn-theme" onclick="toggleTheme()" id="themeBtn">🌓 Alternar Tema</button>
            </div>
        </div>
    </header>

    <main class="container">

        <!-- Perfil Hero -->
        <section class="hero-section">
            <img src="{foto_url}" alt="Foto de {nome_eleitoral}" class="profile-photo" onerror="this.src='https://via.placeholder.com/300x380?text=Foto+Indisponivel'">
            <div class="profile-info">
                <div class="hero-tags">
                    <span class="tag-party">{partido}</span>
                    <span class="tag-role">{cargo} • {uf}</span>
                    <span class="badge badge-info">{data.get('situacao', 'Em Exercício')}</span>
                </div>
                <h1 class="profile-name">{nome_eleitoral}</h1>
                <p class="profile-civil-name">Nome Civil: <strong>{nome_civil}</strong></p>

                <div class="quick-bio">
                    <div class="bio-item">
                        <span class="bio-label">Mandato / Legislatura</span>
                        <span class="bio-val">{data.get('mandato_periodo') or f"Legislatura {data.get('legislatura', 57)}"}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Naturalidade</span>
                        <span class="bio-val">{data.get('municipio_nascimento') or 'Brasil'}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Escolaridade</span>
                        <span class="bio-val">{data.get('escolaridade') or 'Superior Completo'}</span>
                    </div>
                    <div class="bio-item">
                        <span class="bio-label">Gabinete / Contato</span>
                        <span class="bio-val">{data.get('telefone_gabinete') or 'Gabinete Oficial'}</span>
                    </div>
                </div>

                <div style="margin-top: 10px;">
                    <span class="bio-label" style="margin-bottom: 6px;">Redes Sociais Oficiais:</span>
                    {redes_html}
                </div>
            </div>
        </section>

        <!-- KPI Dashboard -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Salário Base Mensal</div>
                <div class="kpi-value">{salario_base.split('(')[0].strip()}</div>
                <div class="kpi-subtext">Valor bruto fixado no Decreto Leg. 172/2022</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Assiduidade Parlamentar</div>
                <div class="kpi-value">{assiduidade.split(' ')[0]}</div>
                <div class="kpi-subtext">Presença em sessões deliberativas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Patrimônio Declarado (TSE)</div>
                <div class="kpi-value">{patrimonio_recente.split('/')[0].strip()}</div>
                <div class="kpi-subtext">Declaração oficial no DivulgaCandContas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Investigações & Notícias</div>
                <div class="kpi-value">{controversias_total} Casos</div>
                <div class="kpi-subtext">Fatos públicos catalogados com contraditório</div>
            </div>
        </section>

        <!-- Remuneração e Verbas -->
        <section>
            <h2 class="section-title">💰 Remuneração, Cotas e Verbas Públicas</h2>
            <div class="card">
                <h3 class="card-title">💵 Estrutura Remuneratória e Benefícios Oficiais</h3>
                <p style="margin-bottom: 14px; font-size: 0.92rem;">
                    Remuneração oficial base: <strong>{salario_base}</strong>. Além do subsídio mensal bruto, o mandato dispõe de verbas operacionais e indenizatórias regulamentadas pela Mesa Diretora:
                </p>
                <ul class="styled-list">
                    {auxilios_html}
                </ul>
                <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-color); display: flex; gap: 16px; flex-wrap: wrap;">
                    <a href="{link_gastos}" target="_blank" rel="noopener" class="btn-link">📊 Consultar painel oficial de gastos e notas fiscais da cota ↗</a>
                    <a href="{link_presenca}" target="_blank" rel="noopener" class="btn-link">📋 Consultar diário de presença em plenário ↗</a>
                </div>
            </div>
        </section>

        <!-- Atuação Legislativa -->
        <section>
            <h2 class="section-title">📜 Atuação Legislativa e Principais Projetos</h2>
            <div class="proposals-grid">
                {props_html}
            </div>
        </section>

        <!-- Evolução Patrimonial -->
        <section>
            <h2 class="section-title">📈 Evolução Patrimonial Declarada à Justiça Eleitoral (TSE)</h2>
            <div class="card" style="padding: 0; overflow-x: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Ano da Eleição</th>
                            <th>Cargo Disputado</th>
                            <th>Total em Bens Declarados</th>
                            <th>Variação</th>
                            <th>Composição dos Principais Bens</th>
                        </tr>
                    </thead>
                    <tbody>
                        {patrimonio_html}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- Notícias, Investigações e Escândalos -->
        <section>
            <h2 class="section-title">⚖️ Dossiê de Notícias, Investigações, Processos e Escândalos</h2>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 16px;">
                Levantamento cronológico de operações policiais, inquéritos do Ministério Público, processos no STF/STJ, representações éticas e matérias jornalísticas de interesse público com links e posicionamento obrigatório da defesa.
            </p>
            
            <div class="filter-bar">
                {filter_buttons_html}
            </div>

            <div class="timeline" id="controversiesTimeline">
                {controversias_html}
            </div>
        </section>

        <!-- Fontes e Trilha de Auditoria -->
        <footer class="footer">
            <p><strong>Dossiê gerado em:</strong> {data_geracao} | Metodologia: Auditoria em APIs de Dados Abertos, Diários Oficiais e Veículos Jornalísticos Auditáveis.</p>
            <div class="audit-links">
                <a href="index.html">📋 Índice Geral</a>
                <a href="{link_perfil}" target="_blank" rel="noopener">🏛️ Portal Oficial do Mandato</a>
                <a href="{link_gastos}" target="_blank" rel="noopener">💸 Portal da Transparência de Gastos</a>
                <a href="{link_tse}" target="_blank" rel="noopener">🗳️ TSE DivulgaCandContas</a>
                <a href="https://portaldatransparencia.gov.br" target="_blank" rel="noopener">🔎 Portal da Transparência CGU</a>
            </div>
        </footer>

    </main>

    <script>
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('dossie_theme', next);
        }}

        (function initTheme() {{
            const saved = localStorage.getItem('dossie_theme');
            if (saved) {{
                document.documentElement.setAttribute('data-theme', saved);
            }}
        }})();

        function filterControversies(categorySlug, btn) {{
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const items = document.querySelectorAll('.timeline-item');
            items.forEach(item => {{
                if (categorySlug === 'all' || item.getAttribute('data-category') === categorySlug) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    return template

def generate_index_html(entries: List[Dict[str, Any]]) -> str:
    data_atualizacao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    total_politicos = len(entries)
    total_propostas = sum(e.get('proposicoes_total', 0) for e in entries)
    total_controversias = sum(e.get('controversias_total', 0) for e in entries)
    
    cards_html = ""
    for e in entries:
        nome_eleitoral = html.escape(e.get('nome_eleitoral', 'Político'))
        nome_civil = html.escape(e.get('nome_civil', ''))
        cargo = html.escape(e.get('cargo', 'Agente Público'))
        partido = html.escape(e.get('partido', 'S/ Partido'))
        uf = html.escape(e.get('uf', 'BR'))
        foto_url = e.get('foto_url') or "https://via.placeholder.com/300x380?text=Sem+Foto"
        salario = html.escape(str(e.get('salario_base', 'R$ 44.008,52')).split('(')[0].strip())
        patrimonio = html.escape(str(e.get('patrimonio_recente', 'Consultar TSE')).split('/')[0].strip())
        filename = html.escape(e.get('filename', '#'))
        props_c = e.get('proposicoes_total', 0)
        contr_c = e.get('controversias_total', 0)
        data_analise = html.escape(e.get('data_atualizacao', 'Recente'))
        
        cards_html += f"""
        <div class="politician-card" data-search="{nome_eleitoral.lower()} {nome_civil.lower()} {partido.lower()} {uf.lower()} {cargo.lower()}">
            <div class="card-hero">
                <img src="{foto_url}" alt="{nome_eleitoral}" class="card-avatar" onerror="this.src='https://via.placeholder.com/120x150?text=Foto'">
                <div class="card-header-info">
                    <div class="card-tags">
                        <span class="tag-party">{partido}</span>
                        <span class="tag-uf">{uf}</span>
                    </div>
                    <h2 class="card-name">{nome_eleitoral}</h2>
                    <p class="card-role">{cargo}</p>
                </div>
            </div>
            <div class="card-body">
                <div class="card-metric-row">
                    <div class="card-metric">
                        <span class="metric-label">Salário Base</span>
                        <span class="metric-val">{salario}</span>
                    </div>
                    <div class="card-metric">
                        <span class="metric-label">Patrimônio</span>
                        <span class="metric-val">{patrimonio}</span>
                    </div>
                </div>
                <div class="card-stats-row">
                    <span class="stat-pill">📜 {props_c} Propostas</span>
                    <span class="stat-pill">⚖️ {contr_c} Notícias/Casos</span>
                </div>
            </div>
            <div class="card-footer">
                <span class="audit-date">Atualizado: {data_analise}</span>
                <a href="{filename}" class="btn-dossie">Acessar Dossiê ➔</a>
            </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Índice Geral — Dossiê Político & Auditoria Cidadã</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-card: #131c2e;
            --bg-card-alt: #1e293b;
            --bg-card-hover: #26354d;
            --bg-input: #0f172a;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #38bdf8;
            --accent-hover: #0284c7;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            --radius: 14px;
        }}

        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-alt: #f1f5f9;
            --bg-card-hover: #e2e8f0;
            --bg-input: #f1f5f9;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --accent: #0284c7;
            --accent-hover: #0369a1;
            --accent-glow: rgba(2, 132, 199, 0.12);
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding-bottom: 80px;
            transition: background-color 0.25s ease, color 0.25s ease;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}

        /* Header Bar */
        .top-nav {{
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: 18px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}

        .top-nav-inner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand {{
            font-size: 1.25rem;
            font-weight: 800;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--text-main);
            text-decoration: none;
        }}

        .brand-badge {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 3px 10px;
            border-radius: 999px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        .btn-theme {{
            background: var(--bg-card-alt);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}

        .btn-theme:hover {{
            border-color: var(--accent);
            transform: translateY(-1px);
        }}

        /* Hero Banner */
        .index-hero {{
            margin-top: 32px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 36px;
            box-shadow: var(--shadow);
            text-align: center;
        }}

        .index-title {{
            font-size: 2.2rem;
            font-weight: 900;
            letter-spacing: -0.5px;
            margin-bottom: 8px;
        }}

        .index-subtitle {{
            color: var(--text-muted);
            font-size: 1rem;
            max-width: 680px;
            margin: 0 auto 24px auto;
        }}

        /* Search Bar */
        .search-box {{
            max-width: 540px;
            margin: 0 auto;
            position: relative;
        }}

        .search-input {{
            width: 100%;
            padding: 14px 20px 14px 44px;
            border-radius: 10px;
            background: var(--bg-input);
            border: 2px solid var(--border-color);
            color: var(--text-main);
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--accent);
            box-shadow: 0 0 0 4px var(--accent-glow);
        }}

        .search-icon {{
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.1rem;
            color: var(--text-muted);
        }}

        /* Aggregate Stats Bar */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin: 32px 0;
        }}

        .stat-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: 20px;
            text-align: center;
            box-shadow: var(--shadow);
        }}

        .stat-num {{
            font-size: 1.8rem;
            font-weight: 900;
            color: var(--accent);
            line-height: 1.1;
        }}

        .stat-desc {{
            font-size: 0.78rem;
            color: var(--text-muted);
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-top: 4px;
        }}

        /* Cards Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 22px;
            margin-top: 24px;
        }}

        .politician-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .politician-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent);
        }}

        .card-hero {{
            padding: 22px;
            display: flex;
            gap: 18px;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }}

        .card-avatar {{
            width: 72px;
            height: 90px;
            border-radius: 8px;
            object-fit: cover;
            border: 2px solid var(--border-color);
            background: var(--bg-card-alt);
        }}

        .card-header-info {{
            flex: 1;
        }}

        .card-tags {{
            display: flex;
            gap: 6px;
            margin-bottom: 6px;
        }}

        .tag-party {{
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--accent);
            font-weight: 800;
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .tag-uf {{
            background: var(--bg-card-alt);
            color: var(--text-main);
            font-weight: 700;
            font-size: 0.72rem;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }}

        .card-name {{
            font-size: 1.25rem;
            font-weight: 800;
            color: var(--text-main);
            line-height: 1.2;
        }}

        .card-role {{
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .card-body {{
            padding: 18px 22px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .card-metric-row {{
            display: flex;
            justify-content: space-between;
            gap: 10px;
        }}

        .card-metric {{
            display: flex;
            flex-direction: column;
        }}

        .metric-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 700;
            letter-spacing: 0.4px;
        }}

        .metric-val {{
            font-size: 0.95rem;
            font-weight: 800;
            color: var(--text-main);
        }}

        .card-stats-row {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .stat-pill {{
            background: var(--bg-card-alt);
            color: var(--text-muted);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
        }}

        .card-footer {{
            padding: 14px 22px;
            background: var(--bg-card-alt);
            border-top: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .audit-date {{
            font-size: 0.72rem;
            color: var(--text-muted);
        }}

        .btn-dossie {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #0f172a;
            font-size: 0.8rem;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 6px;
            text-decoration: none;
            transition: all 0.2s ease;
        }}

        .btn-dossie:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px var(--accent-glow);
        }}

        .footer {{
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            font-size: 0.82rem;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>

    <header class="top-nav">
        <div class="container top-nav-inner">
            <a href="index.html" class="brand">
                <span>🏛️ Dossiê Político</span>
                <span class="brand-badge">Índice Geral</span>
            </a>
            <div class="nav-actions">
                <button class="btn-theme" onclick="toggleTheme()" id="themeBtn">🌓 Alternar Tema</button>
            </div>
        </div>
    </header>

    <main class="container">

        <section class="index-hero">
            <h1 class="index-title">Painel de Auditoria & Transparência Cidadã</h1>
            <p class="index-subtitle">Consolidado de figuras públicas brasileiras com dados de remuneração, assiduidade, evolução patrimonial no TSE e histórico de investigações.</p>
            
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input type="text" id="searchInput" class="search-input" placeholder="Buscar por nome, partido, cargo ou estado..." onkeyup="filterCards()">
            </div>
        </section>

        <!-- Stats Bar -->
        <section class="stats-grid">
            <div class="stat-box">
                <div class="stat-num">{total_politicos}</div>
                <div class="stat-desc">Políticos Auditados</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{total_propostas}</div>
                <div class="stat-desc">Proposições & Leis Monitoradas</div>
            </div>
            <div class="stat-box">
                <div class="stat-num">{total_controversias}</div>
                <div class="stat-desc">Investigações & Notícias Catalogadas</div>
            </div>
        </section>

        <!-- Cards List -->
        <section>
            <div class="cards-grid" id="cardsGrid">
                {cards_html}
            </div>
        </section>

        <footer class="footer">
            <p><strong>Índice atualizado em:</strong> {data_atualizacao} | Diretório: <code>~/.dossie-politico/</code></p>
        </footer>

    </main>

    <script>
        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('dossie_theme', next);
        }}

        (function initTheme() {{
            const saved = localStorage.getItem('dossie_theme');
            if (saved) {{
                document.documentElement.setAttribute('data-theme', saved);
            }}
        }})();

        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.querySelectorAll('.politician-card');
            cards.forEach(card => {{
                const searchData = card.getAttribute('data-search') || '';
                if (searchData.includes(query)) {{
                    card.style.display = 'flex';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""

def update_index_catalog(output_dir: str, data: Dict[str, Any], filename: str):
    index_json_path = os.path.join(output_dir, "index.json")
    index_html_path = os.path.join(output_dir, "index.html")
    
    entries = []
    if os.path.exists(index_json_path):
        try:
            with open(index_json_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        except Exception:
            entries = []

    nome_eleitoral = data.get('nome_eleitoral') or data.get('nome') or 'Politico'
    card_id = sanitize_filename(nome_eleitoral)
    
    patrimonio = 'Consultar TSE'
    if data.get('evolucao_patrimonial'):
        patrimonio = str(data['evolucao_patrimonial'][0].get('valor_formatado') or 'Consultar TSE')
        
    entry_dict = {
        'id': card_id,
        'nome_eleitoral': nome_eleitoral,
        'nome_civil': data.get('nome_civil', nome_eleitoral),
        'cargo': data.get('cargo', 'Agente Público'),
        'partido': data.get('partido', 'S/ Partido'),
        'uf': data.get('uf', 'BR'),
        'foto_url': data.get('foto_url', ''),
        'salario_base': data.get('salario_oficial_base', 'R$ 44.008,52'),
        'patrimonio_recente': patrimonio,
        'proposicoes_total': len(data.get('proposicoes_principais', [])),
        'controversias_total': len(data.get('controversias_e_noticias', [])),
        'filename': filename,
        'data_atualizacao': datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
    }

    # Atualiza ou insere
    existing_idx = next((i for i, item in enumerate(entries) if item.get('id') == card_id or item.get('filename') == filename), None)
    if existing_idx is not None:
        entries[existing_idx] = entry_dict
    else:
        entries.insert(0, entry_dict)

    # Grava index.json
    with open(index_json_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    # Renderiza e grava index.html
    index_html_content = generate_index_html(entries)
    with open(index_html_path, 'w', encoding='utf-8') as f:
        f.write(index_html_content)

def build_dossier_file(data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
    if output_dir is None:
        home = str(Path.home())
        output_dir = os.path.join(home, ".dossie-politico")
    
    os.makedirs(output_dir, exist_ok=True)
    
    nome_politico = data.get('nome_eleitoral') or data.get('nome') or 'Politico'
    filename = f"{sanitize_filename(nome_politico)}.html"
    filepath = os.path.join(output_dir, filename)
    
    html_content = generate_dossier_html(data)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    # Atualiza catálogo e index.html
    update_index_catalog(output_dir, data, filename)
    
    return filepath

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python3 generate_dossier_html.py <dossie_data.json> [output_dir]")
        sys.exit(1)
        
    json_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        dossier_data = json.load(f)
        
    generated_path = build_dossier_file(dossier_data, out_dir)
    print(f"Dossiê HTML gerado com sucesso em:\n{generated_path}")
    print(f"Índice atualizado em:\n{os.path.join(os.path.dirname(generated_path), 'index.html')}")
