"""
pages/relatorio.py
──────────────────
Relatório auditável de um treinamento:
  - Resumo executivo com metadados
  - Tabela de presenças com busca/filtro
  - Exportação: CSV e Excel (.xlsx)
  - Visualização direta pelo organizador
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import (
    listar_treinamentos, buscar_treinamento, listar_presencas,
)
from utils.helpers import (
    exportar_csv, exportar_excel,
    fmt_data, fmt_hora, fmt_carga, fmt_datetime, formatar_cpf,
)
from utils.styles import inject_css, header


def render(tid: str | None = None):
    inject_css()
    header(subtitulo="Relatórios de Treinamentos")

    # Se vier de session_state (clicou no botão do painel)
    if not tid:
        tid = st.session_state.get("relatorio_id")

    if tid:
        _relatorio_treinamento(tid)
    else:
        _lista_treinamentos()


# ═══════════════════════════════════════════════════════════════════
# LISTA DE TODOS OS TREINAMENTOS
# ═══════════════════════════════════════════════════════════════════

def _lista_treinamentos():
    st.markdown("### 📊 Selecione um treinamento para ver o relatório")

    lista = listar_treinamentos()

    if not lista:
        st.info("Nenhum treinamento cadastrado ainda.")
        if st.button("← Ir ao Painel"):
            st.switch_page("app.py")
        return

    for t in lista:
        tid = t["id"]
        enc = bool(t.get("encerrado"))
        n   = t.get("total_presencas", 0)

        col_info, col_btn = st.columns([4, 1])
        with col_info:
            st.markdown(f"""
            <div class="pc-card" style="margin-bottom:0.5rem;">
                <div class="pc-badge {'pc-badge-closed' if enc else 'pc-badge-active'}">
                    {'🔒 Encerrado' if enc else '🟢 Ativo'}
                </div>
                <div class="pc-card-title">{t['nome']}</div>
                <div class="pc-meta">
                    📅 {fmt_data(t.get('data'))} {fmt_hora(t.get('hora'))}
                    &nbsp;·&nbsp; 🏢 {t.get('setor') or '—'}
                    &nbsp;·&nbsp; 👥 <strong>{n}</strong> presença(s)
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_btn:
            if st.button("Ver Relatório →", key=f"ver_{tid}", use_container_width=True):
                st.session_state["relatorio_id"] = tid
                st.rerun()

        st.markdown("---")


# ═══════════════════════════════════════════════════════════════════
# RELATÓRIO DE UM TREINAMENTO
# ═══════════════════════════════════════════════════════════════════

def _relatorio_treinamento(tid: str):
    t = buscar_treinamento(tid)

    if not t:
        st.error("Treinamento não encontrado.")
        if st.button("← Voltar"):
            st.session_state.pop("relatorio_id", None)
            st.rerun()
        return

    presencas = listar_presencas(tid)
    n = len(presencas)
    enc = bool(t.get("encerrado"))

    # ── Navegação ────────────────────────────────────────────────
    if st.button("← Todos os Treinamentos"):
        st.session_state.pop("relatorio_id", None)
        st.rerun()

    # ── Header do Relatório ──────────────────────────────────────
    st.markdown(f"""
    <div class="pc-report-header">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <div class="pc-report-label">Relatório de Presença</div>
                <div class="pc-report-title">{t['nome']}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'DM Serif Display',serif;font-size:3rem;color:#c8440a;line-height:1;">{n}</div>
                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;color:rgba(245,240,232,0.45);">presença(s)</div>
            </div>
        </div>
        <div class="pc-report-meta">
            <div class="pc-report-meta-item"><strong>Data</strong><span>{fmt_data(t.get('data'))} {fmt_hora(t.get('hora'))}</span></div>
            <div class="pc-report-meta-item"><strong>Local</strong><span>{t.get('local') or '—'}</span></div>
            <div class="pc-report-meta-item"><strong>Setor Organizador</strong><span>{t.get('setor') or '—'}</span></div>
            <div class="pc-report-meta-item"><strong>Instrutor</strong><span>{t.get('instrutor') or '—'}</span></div>
            <div class="pc-report-meta-item"><strong>Carga Horária</strong><span>{fmt_carga(t.get('carga_horas'))}</span></div>
            <div class="pc-report-meta-item"><strong>Status</strong><span>{'🔒 Encerrado' if enc else '🟢 Ativo'}</span></div>
            <div class="pc-report-meta-item"><strong>Criado em</strong><span>{fmt_datetime(t.get('criado_em'))}</span></div>
            {f"<div class='pc-report-meta-item'><strong>Encerrado em</strong><span>{fmt_datetime(t.get('encerrado_em'))}</span></div>" if t.get('encerrado_em') else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Descrição ────────────────────────────────────────────────
    if t.get("descricao"):
        with st.expander("📄 Descrição / Objetivos"):
            st.write(t["descricao"])

    # ── Estatísticas ─────────────────────────────────────────────
    emails_dominio = len(set(
        p["email"].split("@")[1] for p in presencas if "@" in (p.get("email") or "")
    ))
    com_cargo     = sum(1 for p in presencas if p.get("cargo"))
    com_matricula = sum(1 for p in presencas if p.get("matricula"))

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, n, "Presenças"),
        (c2, emails_dominio, "Domínios de E-mail"),
        (c3, com_cargo, "Com Cargo"),
        (c4, com_matricula, "Com Matrícula"),
    ]:
        col.markdown(f"""
        <div class="pc-stat">
            <div class="pc-stat-value">{val}</div>
            <div class="pc-stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Ações de exportação ──────────────────────────────────────
    col_exp1, col_exp2, col_exp3, _ = st.columns([1, 1, 1, 3])

    nome_arquivo = t["nome"].replace(" ", "-").lower()
    data_arquivo = (t.get("data") or datetime.now().strftime("%Y-%m-%d"))

    csv_data = exportar_csv(t, presencas)
    col_exp1.download_button(
        "⬇ CSV",
        data=csv_data,
        file_name=f"presencas_{nome_arquivo}_{data_arquivo}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    try:
        xlsx_data = exportar_excel(t, presencas)
        col_exp2.download_button(
            "📊 Excel",
            data=xlsx_data,
            file_name=f"presencas_{nome_arquivo}_{data_arquivo}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except Exception as ex:
        col_exp2.warning(f"Excel indisponível: {ex}")

    if col_exp3.button("🖨 Imprimir", use_container_width=True):
        st.info("Use Ctrl+P / Cmd+P no navegador para imprimir esta página.")

    st.markdown('<hr class="pc-divider">', unsafe_allow_html=True)

    # ── Tabela de Presenças ──────────────────────────────────────
    st.markdown(f"### 👥 Lista de Presença ({n} participante(s))")

    if not presencas:
        st.info("Nenhuma presença registrada ainda.")
        return

    # Busca
    busca = st.text_input(
        "🔍 Buscar por nome, CPF ou e-mail",
        placeholder="Digite para filtrar...",
        key="busca_relatorio",
    )

    # Monta DataFrame
    df = pd.DataFrame([
        {
            "#": i + 1,
            "Nome Completo":     p.get("nome", ""),
            "CPF":               formatar_cpf(p.get("cpf", "")),
            "E-mail":            p.get("email", ""),
            "Cargo/Função":      p.get("cargo") or "—",
            "Matrícula":         p.get("matricula") or "—",
            "Data/Hora Registro": fmt_datetime(p.get("registrado_em")),
        }
        for i, p in enumerate(presencas)
    ])

    # Aplica filtro de busca
    if busca.strip():
        q = busca.strip().lower()
        mask = (
            df["Nome Completo"].str.lower().str.contains(q, na=False) |
            df["CPF"].str.lower().str.contains(q, na=False) |
            df["E-mail"].str.lower().str.contains(q, na=False)
        )
        df_filtrado = df[mask].reset_index(drop=True)
        df_filtrado["#"] = range(1, len(df_filtrado) + 1)
    else:
        df_filtrado = df

    if df_filtrado.empty:
        st.warning("Nenhum resultado encontrado para a busca.")
    else:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "#":               st.column_config.NumberColumn(width="small"),
                "Nome Completo":   st.column_config.TextColumn(width="large"),
                "CPF":             st.column_config.TextColumn(width="medium"),
                "E-mail":          st.column_config.TextColumn(width="large"),
                "Cargo/Função":    st.column_config.TextColumn(width="medium"),
                "Matrícula":       st.column_config.TextColumn(width="small"),
                "Data/Hora Registro": st.column_config.TextColumn(width="medium"),
            },
        )

        st.markdown(
            f"<p style='font-size:0.75rem;color:#7a7268;text-align:right;margin-top:0.5rem;'>"
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} — PresençaCerta"
            f"</p>",
            unsafe_allow_html=True,
        )
