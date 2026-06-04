"""
pages/presenca.py
─────────────────
Página de registro de presença — acessada pelo colaborador
via QR Code ou link direto.

URL: /?page=presenca&id=<treinamento_id>
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import datetime
from utils.database import buscar_treinamento, registrar_presenca
from utils.helpers import (
    validar_cpf, validar_email, nome_completo,
    formatar_cpf, fmt_data, fmt_hora, fmt_datetime,
)
from utils.styles import inject_css, header


def render(tid: str):
    inject_css()

    # ── Cabeçalho mínimo ────────────────────────────────────────
    st.markdown("""
    <div class="pc-header" style="padding:1rem 1.5rem;margin-bottom:1rem;">
        <div class="pc-logo" style="font-size:1.3rem;">Presença<span>Certa</span></div>
        <div class="pc-subtitle">Registro de Presença em Treinamento</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Carrega treinamento ──────────────────────────────────────
    if not tid:
        _erro("Link inválido. Nenhum treinamento identificado.")
        return

    t = buscar_treinamento(tid)

    if not t:
        _erro("Treinamento não encontrado. Verifique o link ou entre em contato com o organizador.")
        return

    # ── Informações do treinamento ───────────────────────────────
    enc = bool(t.get("encerrado"))
    data_fmt = fmt_data(t.get("data"))
    hora_fmt = fmt_hora(t.get("hora"))

    st.markdown(f"""
    <div class="pc-report-header" style="padding:1.25rem 1.5rem;margin-bottom:1.25rem;">
        <div class="pc-report-label">Registro de Presença</div>
        <div class="pc-report-title">{t['nome']}</div>
        <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin-top:0.75rem;font-size:0.85rem;color:rgba(245,240,232,0.65);">
            <span>📅 {data_fmt} {hora_fmt}</span>
            <span>🏢 {t.get('setor') or '—'}</span>
            <span>📍 {t.get('local') or '—'}</span>
            {f"<span>👤 {t.get('instrutor')}</span>" if t.get('instrutor') else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Treinamento encerrado ────────────────────────────────────
    if enc:
        st.markdown("""
        <div class="pc-encerrado-alert">
            ⚠️ <strong>Este treinamento está encerrado.</strong>
            Não é mais possível registrar presenças. Entre em contato com o setor organizador.
        </div>
        """, unsafe_allow_html=True)
        return

    # ── Formulário (single-session state) ───────────────────────
    if st.session_state.get(f"presenca_ok_{tid}"):
        _sucesso(tid, t)
        return

    _formulario(tid, t)


def _formulario(tid: str, t: dict):
    st.markdown(
        "<p style='font-size:0.9rem;color:#7a7268;margin-bottom:1rem;'>Preencha seus dados abaixo para confirmar sua presença neste treinamento.</p>",
        unsafe_allow_html=True,
    )

    with st.form("form_presenca", clear_on_submit=False):
        nome = st.text_input(
            "Nome Completo *",
            placeholder="Digite seu nome e sobrenome",
            key="pres_nome",
        )

        col1, col2 = st.columns(2)
        cpf = col1.text_input(
            "CPF *",
            placeholder="000.000.000-00",
            max_chars=14,
            key="pres_cpf",
        )
        email = col2.text_input(
            "E-mail Corporativo *",
            placeholder="seunome@empresa.com.br",
            key="pres_email",
        )

        col3, col4 = st.columns(2)
        cargo = col3.text_input(
            "Cargo / Função",
            placeholder="Ex: Técnico de Segurança",
            key="pres_cargo",
        )
        matricula = col4.text_input(
            "Matrícula",
            placeholder="Número de matrícula (opcional)",
            key="pres_matricula",
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button(
            "✓  Confirmar Minha Presença",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            _processar(tid, t, nome, cpf, email, cargo, matricula)

    st.markdown(
        "<p style='font-size:0.75rem;color:#7a7268;text-align:center;margin-top:0.75rem;'>"
        "Ao confirmar, você declara estar presente neste treinamento. "
        "Os dados são usados exclusivamente para fins de registro e auditoria."
        "</p>",
        unsafe_allow_html=True,
    )


def _processar(tid, t, nome, cpf, email, cargo, matricula):
    erros = []

    if not nome_completo(nome):
        erros.append("Informe seu **nome completo** (nome e sobrenome).")

    # Formata CPF antes de validar
    cpf_fmt = formatar_cpf(cpf) if cpf else ""
    if not validar_cpf(cpf):
        erros.append("CPF inválido. Verifique e tente novamente.")

    if not validar_email(email):
        erros.append("E-mail inválido. Informe um endereço corporativo válido.")

    if erros:
        for e in erros:
            st.error(e)
        return

    with st.spinner("Registrando presença..."):
        ok, msg = registrar_presenca(tid, {
            "nome": nome.strip(),
            "cpf": cpf_fmt,
            "email": email.strip().lower(),
            "cargo": cargo.strip() or None,
            "matricula": matricula.strip() or None,
        })

    if ok:
        st.session_state[f"presenca_ok_{tid}"] = {
            "nome": nome.strip(),
            "cpf": cpf_fmt,
            "email": email.strip().lower(),
            "cargo": cargo.strip() or None,
            "matricula": matricula.strip() or None,
            "ts": datetime.now().strftime("%d/%m/%Y às %H:%M"),
        }
        st.rerun()
    else:
        st.error(f"❌ {msg}")


def _sucesso(tid: str, t: dict):
    dados = st.session_state[f"presenca_ok_{tid}"]

    st.markdown(f"""
    <div class="pc-success-box">
        <div class="pc-success-icon">✓</div>
        <div class="pc-success-title">Presença Confirmada!</div>
        <p style="font-size:0.9rem;margin-top:0.25rem;">
            Sua participação foi registrada com sucesso.
        </p>
        <div class="pc-receipt">
            <div class="pc-receipt-row"><strong>Treinamento</strong>{t['nome']}</div>
            <div class="pc-receipt-row"><strong>Colaborador</strong>{dados['nome']}</div>
            <div class="pc-receipt-row"><strong>CPF</strong>{dados['cpf']}</div>
            <div class="pc-receipt-row"><strong>E-mail</strong>{dados['email']}</div>
            {f"<div class='pc-receipt-row'><strong>Cargo</strong>{dados['cargo']}</div>" if dados.get('cargo') else ""}
        </div>
        <p style="font-size:0.75rem;margin-top:0.75rem;opacity:0.65;">
            Registrado em: {dados['ts']}
        </p>
    </div>
    """, unsafe_allow_html=True)


def _erro(msg: str):
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 1rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">⚠️</div>
        <h2 style="font-family:'DM Serif Display',serif;color:#c0392b;margin-bottom:0.5rem;">Treinamento não encontrado</h2>
        <p style="color:#7a7268;font-size:0.9rem;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)
