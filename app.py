"""
app.py
──────
Ponto de entrada da aplicação PresençaCerta.

Roteamento via query params:
  /?page=presenca&id=<tid>  → Página de registro de presença (colaborador)
  /                         → Painel do organizador
  /?page=relatorio&id=<tid> → Relatório de um treinamento

Navegação interna entre páginas do organizador feita
via st.navigation + sidebar.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from utils.database import init_db
from utils.styles import inject_css

# ── Configuração da Página ───────────────────────────────────────
st.set_page_config(
    page_title="PresençaCerta",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "**PresençaCerta** — Sistema de Controle de Presença em Treinamentos",
    },
)

# ── Inicializa banco de dados ────────────────────────────────────
@st.cache_resource
def inicializar_bd():
    init_db()
    return True

inicializar_bd()

# ── Roteamento por Query Params ──────────────────────────────────
params = st.query_params

page = params.get("page", "painel").lower()
tid  = params.get("id", "")

# ════════════════════════════════════════════════════════════════════
# ROTA: Presença (colaborador — sem sidebar)
# ════════════════════════════════════════════════════════════════════
if page == "presenca":
    from pages.presenca import render as render_presenca
    render_presenca(tid)
    st.stop()

# ════════════════════════════════════════════════════════════════════
# ROTAS DO ORGANIZADOR (com sidebar)
# ════════════════════════════════════════════════════════════════════

inject_css()

# Sidebar de navegação
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem;">
        <div style="font-family:'DM Serif Display',serif;font-size:1.25rem;color:#f5f0e8;">
            Presença<span style="color:#c8440a;">Certa</span>
        </div>
        <div style="font-size:0.75rem;color:rgba(245,240,232,0.45);margin-top:0.15rem;">
            Sistema de Controle de Presença
        </div>
    </div>
    <hr style="border-color:rgba(245,240,232,0.1);margin:0.75rem 0;">
    """, unsafe_allow_html=True)

    opcao_nav = st.radio(
        "Navegação",
        options=["📋 Painel", "📊 Relatórios"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <hr style="border-color:rgba(245,240,232,0.1);margin:1.5rem 0 0.75rem;">
    <div style="font-size:0.72rem;color:rgba(245,240,232,0.3);padding-bottom:1rem;">
        PresençaCerta v1.0<br>
        Dados armazenados localmente
    </div>
    """, unsafe_allow_html=True)

# ── Despacha para a página correta ──────────────────────────────

if page == "relatorio" or opcao_nav == "📊 Relatórios":
    from pages.relatorio import render as render_relatorio
    render_relatorio(tid or None)

else:
    from pages.painel import render as render_painel
    render_painel()
