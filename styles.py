"""
utils/styles.py
───────────────
CSS global injetado via st.markdown para toda a aplicação.
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --ink:    #0f0e0c;
    --paper:  #f5f0e8;
    --cream:  #ede8dc;
    --accent: #c8440a;
    --accent-light: #f4e4dc;
    --muted:  #7a7268;
    --border: #d4cec2;
    --success: #2d6a4f;
    --success-light: #d8f0e6;
    --card: #faf8f4;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Oculta elementos padrão do Streamlit ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Padding do container principal ── */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1000px;
}

/* ── Botões ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    transition: all 0.2s !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 4px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
}

[data-testid="stSidebar"] * {
    color: var(--paper) !important;
}

[data-testid="stSidebar"] .stSelectbox > label,
[data-testid="stSidebar"] p {
    color: rgba(245,240,232,0.7) !important;
}

/* ── Componentes customizados ── */
.pc-header {
    background: #0f0e0c;
    color: #f5f0e8;
    padding: 1.5rem 2rem;
    border-radius: 10px;
    border-bottom: 3px solid #c8440a;
    margin-bottom: 1.5rem;
}

.pc-logo {
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    margin-bottom: 0.25rem;
}

.pc-logo span { color: #c8440a; }

.pc-subtitle {
    font-size: 0.85rem;
    color: rgba(245,240,232,0.55);
}

.pc-card {
    background: #faf8f4;
    border: 1.5px solid #d4cec2;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}

.pc-card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    margin-bottom: 0.3rem;
}

.pc-meta {
    font-size: 0.82rem;
    color: #7a7268;
}

.pc-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}

.pc-badge-active   { background: #f4e4dc; color: #c8440a; }
.pc-badge-closed   { background: #e0ddd8; color: #6a6660; }

.pc-stat {
    background: #faf8f4;
    border: 1.5px solid #d4cec2;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    text-align: center;
}

.pc-stat-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2.25rem;
    color: #c8440a;
    line-height: 1;
}

.pc-stat-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #7a7268;
    margin-top: 0.2rem;
}

.pc-report-header {
    background: #0f0e0c;
    color: #f5f0e8;
    border-radius: 10px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    border-bottom: 3px solid #c8440a;
}

.pc-report-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.75rem;
    margin-bottom: 0.25rem;
}

.pc-report-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #c8440a;
    margin-bottom: 0.35rem;
}

.pc-report-meta {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.75rem;
    margin-top: 1.25rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(245,240,232,0.15);
}

.pc-report-meta-item strong {
    display: block;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: rgba(245,240,232,0.45);
    margin-bottom: 0.15rem;
}

.pc-report-meta-item span {
    font-size: 0.875rem;
    color: #f5f0e8;
}

.pc-success-box {
    background: #d8f0e6;
    border: 1.5px solid #a8d8be;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
    color: #1e4d38;
}

.pc-success-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }

.pc-success-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    margin-bottom: 0.35rem;
}

.pc-receipt {
    background: #ede8dc;
    border: 1.5px solid #d4cec2;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    text-align: left;
    margin-top: 1rem;
    font-size: 0.875rem;
}

.pc-receipt strong {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #7a7268;
    display: block;
    margin-bottom: 0.1rem;
}

.pc-receipt-row { margin-bottom: 0.65rem; }

.pc-encerrado-alert {
    background: #fef3e2;
    border: 1.5px solid #f0c080;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    color: #7a4a10;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.pc-divider {
    border: none;
    border-top: 1.5px solid #d4cec2;
    margin: 1.5rem 0;
}

.pc-nav-link {
    color: rgba(245,240,232,0.7);
    text-decoration: none;
    font-size: 0.85rem;
    display: block;
    padding: 0.4rem 0;
    border-radius: 4px;
    transition: color 0.2s;
}

.pc-nav-link:hover { color: #f5f0e8; }
.pc-nav-link.active { color: #c8440a; font-weight: 600; }

/* Dataframe/tabela */
[data-testid="stDataFrame"] {
    border: 1.5px solid #d4cec2 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}

/* Torna st.info / st.success mais elegante */
.stAlert {
    border-radius: 6px !important;
}
</style>
"""


def inject_css():
    """Injetar CSS global na página."""
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def header(titulo: str = "", subtitulo: str = ""):
    """Renderiza o cabeçalho padrão PresençaCerta."""
    import streamlit as st
    sub_html = f'<div class="pc-subtitle">{subtitulo}</div>' if subtitulo else ""
    st.markdown(f"""
    <div class="pc-header">
        <div class="pc-logo">Presença<span>Certa</span></div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)
