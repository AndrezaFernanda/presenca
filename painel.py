"""
pages/painel.py
───────────────
Painel do Organizador — layout de duas colunas:
  ├── Coluna ESQUERDA: formulário de criação / edição do evento
  └── Coluna DIREITA:  QR Code + link do evento selecionado

Fluxo:
  1. Sidebar lista todos os treinamentos
  2. Clicar em um treinamento o seleciona → preenche formulário + mostra QR
  3. "Novo Treinamento" limpa a seleção e abre formulário em branco
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import date, time, datetime
from utils.database import (
    listar_treinamentos, buscar_treinamento,
    criar_treinamento, atualizar_treinamento,
    encerrar_treinamento, excluir_treinamento,
)
from utils.helpers import (
    gerar_qr_bytes, link_presenca,
    fmt_data, fmt_hora, fmt_carga, fmt_datetime,
)
from utils.styles import inject_css


# ═══════════════════════════════════════════════════════════════════
# ENTRADA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════

def render():
    inject_css()
    _estilos_extras()

    # ── Cabeçalho ───────────────────────────────────────────────
    st.markdown("""
    <div class="pc-header">
        <div class="pc-logo">Presença<span>Certa</span></div>
        <div class="pc-subtitle">Painel do Organizador</div>
    </div>
    """, unsafe_allow_html=True)

    lista = listar_treinamentos()

    # ── Barra superior: seletor de evento + botão Novo ──────────
    _barra_selecao(lista)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Layout principal: col esquerda | col direita ─────────────
    col_form, col_qr = st.columns([1.1, 0.9], gap="large")

    tid_sel = st.session_state.get("tid_selecionado")
    t_sel   = buscar_treinamento(tid_sel) if tid_sel else None

    with col_form:
        _coluna_formulario(t_sel)

    with col_qr:
        _coluna_qr(t_sel, lista)


# ═══════════════════════════════════════════════════════════════════
# BARRA DE SELEÇÃO DE EVENTO
# ═══════════════════════════════════════════════════════════════════

def _barra_selecao(lista: list):
    c_sel, c_novo = st.columns([3, 1], gap="small")

    with c_sel:
        if lista:
            opcoes_ids   = [t["id"]   for t in lista]
            opcoes_nomes = [
                f"{'🔒' if t.get('encerrado') else '🟢'}  {t['nome']}  "
                f"({fmt_data(t.get('data'))})"
                for t in lista
            ]

            # Índice atual baseado no session_state
            tid_atual = st.session_state.get("tid_selecionado")
            idx_atual = opcoes_ids.index(tid_atual) if tid_atual in opcoes_ids else 0

            escolha = st.selectbox(
                "Selecionar evento",
                options=range(len(opcoes_ids)),
                format_func=lambda i: opcoes_nomes[i],
                index=idx_atual,
                label_visibility="collapsed",
                key="selectbox_evento",
            )
            novo_tid = opcoes_ids[escolha]
            if novo_tid != st.session_state.get("tid_selecionado"):
                st.session_state["tid_selecionado"] = novo_tid
                st.session_state.pop("form_editando", None)
                st.rerun()
        else:
            st.info("Nenhum treinamento cadastrado. Crie o primeiro →")

    with c_novo:
        if st.button("➕  Novo Evento", use_container_width=True, type="primary"):
            st.session_state.pop("tid_selecionado", None)
            st.session_state.pop("form_editando", None)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
# COLUNA ESQUERDA — FORMULÁRIO
# ═══════════════════════════════════════════════════════════════════

def _coluna_formulario(t: dict | None):
    criando = t is None
    editando = st.session_state.get("form_editando", False)
    enc = bool(t.get("encerrado")) if t else False

    # ── Título da coluna ────────────────────────────────────────
    if criando:
        st.markdown('<div class="painel-col-title">✏️ Novo Evento</div>', unsafe_allow_html=True)
    elif editando:
        st.markdown('<div class="painel-col-title">✏️ Editar Evento</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="painel-col-title">📋 Informações do Evento</div>', unsafe_allow_html=True)

    # ── Modo visualização (não editando) ─────────────────────────
    if t and not editando:
        _visualizar_evento(t)
        return

    # ── Modo edição / criação ────────────────────────────────────
    _form_evento(t)


def _visualizar_evento(t: dict):
    """Exibe as informações do evento em modo leitura com botões de ação."""
    enc = bool(t.get("encerrado"))
    tid = t["id"]

    badge_cls   = "pc-badge-closed" if enc else "pc-badge-active"
    badge_label = "🔒 Encerrado"    if enc else "🟢 Ativo"

    st.markdown(f"""
    <div class="pc-card" style="margin-bottom:1rem;">
        <div class="pc-badge {badge_cls}" style="margin-bottom:0.6rem;">{badge_label}</div>
        <div class="pc-card-title" style="font-size:1.3rem;margin-bottom:1rem;">{t['nome']}</div>
        <table class="info-table">
            <tr><td class="info-label">📅 Data</td>
                <td>{fmt_data(t.get('data'))} {fmt_hora(t.get('hora'))}</td></tr>
            <tr><td class="info-label">📍 Local</td>
                <td>{t.get('local') or '—'}</td></tr>
            <tr><td class="info-label">🏢 Setor</td>
                <td>{t.get('setor') or '—'}</td></tr>
            <tr><td class="info-label">👤 Instrutor</td>
                <td>{t.get('instrutor') or '—'}</td></tr>
            <tr><td class="info-label">⏱ Carga</td>
                <td>{fmt_carga(t.get('carga_horas'))}</td></tr>
            <tr><td class="info-label">📆 Criado</td>
                <td>{fmt_datetime(t.get('criado_em'))}</td></tr>
        </table>
        {f'<div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid var(--border);font-size:0.875rem;color:#555;">{t["descricao"]}</div>' if t.get('descricao') else ''}
    </div>
    """, unsafe_allow_html=True)

    # ── Botões de ação ───────────────────────────────────────────
    if not enc:
        c1, c2 = st.columns(2)
        if c1.button("✏️ Editar", key=f"edit_btn_{tid}", use_container_width=True, type="primary"):
            st.session_state["form_editando"] = True
            st.rerun()

        if c2.button("🔒 Encerrar", key=f"enc_btn_{tid}", use_container_width=True):
            st.session_state[f"confirm_enc_{tid}"] = True
            st.rerun()
    else:
        if st.button("✏️ Editar mesmo encerrado", key=f"edit_enc_{tid}", use_container_width=True):
            st.session_state["form_editando"] = True
            st.rerun()

    # Confirmação encerrar
    if st.session_state.get(f"confirm_enc_{tid}"):
        st.warning("⚠️ Novas presenças não serão aceitas após encerrar. Confirmar?")
        cc1, cc2 = st.columns(2)
        if cc1.button("Sim, encerrar", key=f"enc_sim_{tid}", type="primary"):
            encerrar_treinamento(tid)
            st.session_state.pop(f"confirm_enc_{tid}", None)
            st.session_state.pop("form_editando", None)
            st.rerun()
        if cc2.button("Cancelar", key=f"enc_nao_{tid}"):
            st.session_state.pop(f"confirm_enc_{tid}", None)
            st.rerun()

    st.markdown('<hr class="pc-divider">', unsafe_allow_html=True)

    # Excluir (com confirmação)
    with st.expander("⚠️ Zona de Perigo"):
        st.warning("Excluir remove **todas as presenças** permanentemente.")
        if st.button("🗑 Excluir este treinamento", key=f"del_btn_{tid}", use_container_width=True):
            st.session_state[f"confirm_del_{tid}"] = True
            st.rerun()
        if st.session_state.get(f"confirm_del_{tid}"):
            st.error("Tem certeza? Esta ação **não pode ser desfeita**.")
            dd1, dd2 = st.columns(2)
            if dd1.button("Confirmar exclusão", key=f"del_sim_{tid}", type="primary"):
                excluir_treinamento(tid)
                st.session_state.pop(f"confirm_del_{tid}", None)
                st.session_state.pop("tid_selecionado", None)
                st.rerun()
            if dd2.button("Cancelar", key=f"del_nao_{tid}"):
                st.session_state.pop(f"confirm_del_{tid}", None)
                st.rerun()


def _form_evento(t: dict | None):
    """Formulário unificado para criar ou editar um treinamento."""
    criando = t is None
    tid     = t["id"] if t else None

    # Valores padrão (edição: usa dados existentes; criação: padrões vazios)
    def _v(campo, fallback=None):
        return t.get(campo) if t else fallback

    # Pré-processa data e hora para os widgets
    data_val = None
    if _v("data"):
        try:
            data_val = date.fromisoformat(str(_v("data"))[:10])
        except Exception:
            data_val = date.today()

    hora_val = None
    if _v("hora"):
        try:
            partes = str(_v("hora"))[:5].split(":")
            hora_val = time(int(partes[0]), int(partes[1]))
        except Exception:
            hora_val = None

    carga_val = float(_v("carga_horas")) if _v("carga_horas") else None

    with st.form(f"form_evento_{'criar' if criando else tid}", clear_on_submit=False):

        nome = st.text_input(
            "Nome do Evento *",
            value=_v("nome", ""),
            placeholder="Ex: NR-35 — Trabalho em Altura",
        )

        c1, c2 = st.columns(2)
        setor     = c1.text_input("Setor Organizador *", value=_v("setor", ""), placeholder="Ex: SESMT / RH")
        instrutor = c2.text_input("Instrutor",           value=_v("instrutor", ""), placeholder="Nome do responsável")

        c3, c4, c5 = st.columns([1.3, 0.8, 0.8])
        data_t = c3.date_input("Data *",           value=data_val or date.today())
        hora_t = c4.time_input("Horário",           value=hora_val)
        carga  = c5.number_input("Carga (h)",       value=carga_val, min_value=0.5, max_value=999.0, step=0.5, format="%.1f")

        local = st.text_input("Local", value=_v("local", ""), placeholder="Ex: Sala B / Online / Teams")

        descricao = st.text_area(
            "Descrição / Objetivos",
            value=_v("descricao", ""),
            placeholder="Breve descrição do treinamento...",
            height=100,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        c_sub, c_can = st.columns(2)
        label_btn = "✓ Criar Evento" if criando else "💾 Salvar Alterações"
        submitted = c_sub.form_submit_button(label_btn, type="primary", use_container_width=True)
        cancelar  = c_can.form_submit_button("✕ Cancelar", use_container_width=True)

        if cancelar:
            st.session_state.pop("form_editando", None)
            if criando:
                pass  # fica na tela de seleção
            st.rerun()

        if submitted:
            erros = []
            if not nome.strip():
                erros.append("Nome do evento é obrigatório.")
            if not setor.strip():
                erros.append("Setor organizador é obrigatório.")

            if erros:
                for e in erros:
                    st.error(e)
            else:
                dados = {
                    "nome":       nome.strip(),
                    "setor":      setor.strip(),
                    "data":       data_t.isoformat() if data_t else None,
                    "hora":       hora_t.strftime("%H:%M") if hora_t else None,
                    "local":      local.strip() or None,
                    "instrutor":  instrutor.strip() or None,
                    "descricao":  descricao.strip() or None,
                    "carga_horas": carga or None,
                }
                try:
                    if criando:
                        novo_tid = criar_treinamento(dados)
                        st.session_state["tid_selecionado"] = novo_tid
                        st.session_state.pop("form_editando", None)
                        st.toast("✅ Evento criado com sucesso!", icon="🎉")
                    else:
                        atualizar_treinamento(tid, dados)
                        st.session_state.pop("form_editando", None)
                        st.toast("💾 Alterações salvas!", icon="✅")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Erro: {ex}")


# ═══════════════════════════════════════════════════════════════════
# COLUNA DIREITA — QR CODE
# ═══════════════════════════════════════════════════════════════════

def _coluna_qr(t: dict | None, lista: list):
    st.markdown('<div class="painel-col-title">📱 QR Code & Link</div>', unsafe_allow_html=True)

    if t is None:
        st.markdown("""
        <div class="pc-card" style="text-align:center;padding:2.5rem 1rem;color:var(--muted);">
            <div style="font-size:3rem;margin-bottom:0.75rem;">📱</div>
            <p style="font-size:0.9rem;">
                Selecione ou crie um evento para<br>visualizar o QR Code e o link de presença.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    tid  = t["id"]
    link = link_presenca(tid)
    enc  = bool(t.get("encerrado"))

    # ── Aviso se encerrado ───────────────────────────────────────
    if enc:
        st.markdown("""
        <div class="pc-encerrado-alert">
            🔒 Este evento está <strong>encerrado</strong>.
            O QR Code ainda pode ser visualizado, mas não aceita novas presenças.
        </div>
        """, unsafe_allow_html=True)

    # ── QR Code ──────────────────────────────────────────────────
    with st.container(border=True):
        try:
            qr_bytes = gerar_qr_bytes(link, tamanho=300)
            st.image(qr_bytes, use_container_width=True, caption="Escaneie para registrar presença")
        except Exception as ex:
            st.warning(f"Não foi possível gerar o QR Code: {ex}")

    # ── Link ─────────────────────────────────────────────────────
    st.markdown("**🔗 Link direto**")
    st.code(link, language=None)

    # ── Botões ───────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    try:
        qr_bytes = gerar_qr_bytes(link)
        c1.download_button(
            "⬇ Baixar QR Code",
            data=qr_bytes,
            file_name=f"qr-{t['nome'].replace(' ', '-').lower()}.png",
            mime="image/png",
            use_container_width=True,
            key=f"dl_qr_{tid}",
        )
    except Exception:
        pass

    if c2.button("📊 Ver Relatório", key=f"qr_rel_{tid}", use_container_width=True):
        st.session_state["relatorio_id"] = tid
        st.switch_page("pages/relatorio.py")

    # ── Estatísticas rápidas ─────────────────────────────────────
    n_pres = t.get("total_presencas", 0)
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.markdown(f"""
    <div class="pc-stat">
        <div class="pc-stat-value">{n_pres}</div>
        <div class="pc-stat-label">Presenças</div>
    </div>""", unsafe_allow_html=True)

    # Reconstrói total de presenças via lista (que já traz o count)
    lista_ids = {x["id"]: x for x in lista}
    t_full = lista_ids.get(tid, t)
    m2.markdown(f"""
    <div class="pc-stat">
        <div class="pc-stat-value">{'🔒' if enc else '🟢'}</div>
        <div class="pc-stat-label">{'Encerrado' if enc else 'Ativo'}</div>
    </div>""", unsafe_allow_html=True)

    # ── Instruções ───────────────────────────────────────────────
    with st.expander("ℹ️ Como usar"):
        st.markdown("""
        1. **Projete** o QR Code em tela durante o treinamento, **ou**
        2. **Envie o link** por e-mail para os participantes
        3. Cada colaborador acessa, preenche **nome, CPF e e-mail**
        4. A presença é registrada automaticamente
        5. Acesse **📊 Relatório** para exportar CSV/Excel
        """)


# ═══════════════════════════════════════════════════════════════════
# CSS ADICIONAL ESPECÍFICO DO PAINEL
# ═══════════════════════════════════════════════════════════════════

def _estilos_extras():
    st.markdown("""
    <style>
    .painel-col-title {
        font-family: 'DM Serif Display', serif;
        font-size: 1.15rem;
        color: var(--ink);
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--accent);
        margin-bottom: 1rem;
    }

    .info-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.875rem;
    }

    .info-table tr td {
        padding: 0.45rem 0.5rem;
        border-bottom: 1px solid var(--border);
        vertical-align: top;
    }

    .info-table tr:last-child td { border-bottom: none; }

    .info-label {
        font-weight: 600;
        color: var(--muted);
        white-space: nowrap;
        width: 110px;
        font-size: 0.8rem;
    }

    /* Remove padding excessivo do selectbox no topo */
    [data-testid="stSelectbox"] { margin-bottom: 0; }

    /* Alinha os títulos de coluna */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        height: 100%;
    }
    </style>
    """, unsafe_allow_html=True)
