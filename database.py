"""
utils/database.py
─────────────────
Camada de abstração de banco de dados.
Suporta SQLite (padrão, zero config) e PostgreSQL.

Configuração via variáveis de ambiente ou .streamlit/secrets.toml
"""

import os
import sqlite3
import contextlib
from datetime import datetime
from typing import Optional

# ── Carrega .env se existir ──────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "presencacerta.db")


# ═══════════════════════════════════════════════════════════════════
# CONEXÃO
# ═══════════════════════════════════════════════════════════════════

def _get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _get_postgres_conn():
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise RuntimeError("psycopg2-binary não instalado. Execute: pip install psycopg2-binary")

    # Tenta Streamlit Secrets primeiro, depois env vars
    try:
        import streamlit as st
        cfg = st.secrets.get("postgres", {})
        host = cfg.get("host", os.getenv("POSTGRES_HOST", "localhost"))
        port = cfg.get("port", os.getenv("POSTGRES_PORT", 5432))
        db   = cfg.get("db",   os.getenv("POSTGRES_DB",   "presencacerta"))
        user = cfg.get("user", os.getenv("POSTGRES_USER", "postgres"))
        pwd  = cfg.get("password", os.getenv("POSTGRES_PASSWORD", ""))
    except Exception:
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", 5432)
        db   = os.getenv("POSTGRES_DB",   "presencacerta")
        user = os.getenv("POSTGRES_USER", "postgres")
        pwd  = os.getenv("POSTGRES_PASSWORD", "")

    conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)
    conn.autocommit = False
    return conn


@contextlib.contextmanager
def get_conn():
    """Context manager que entrega uma conexão e faz commit/rollback automaticamente."""
    if DB_TYPE == "postgres":
        conn = _get_postgres_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = _get_sqlite_conn()
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()


def ph(n: int = 1) -> str:
    """Retorna placeholders corretos: ? (SQLite) ou %s (PostgreSQL)."""
    p = "%s" if DB_TYPE == "postgres" else "?"
    return ", ".join([p] * n)


def p() -> str:
    """Placeholder único."""
    return "%s" if DB_TYPE == "postgres" else "?"


# ═══════════════════════════════════════════════════════════════════
# INICIALIZAÇÃO DO SCHEMA
# ═══════════════════════════════════════════════════════════════════

def init_db():
    """Cria as tabelas se não existirem (idempotente)."""
    if DB_TYPE == "postgres":
        _init_postgres()
    else:
        _init_sqlite()


def _init_sqlite():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS treinamentos (
                id          TEXT PRIMARY KEY,
                nome        TEXT NOT NULL,
                data        TEXT,
                hora        TEXT,
                local       TEXT,
                setor       TEXT NOT NULL,
                instrutor   TEXT,
                descricao   TEXT,
                carga_horas REAL,
                encerrado   INTEGER NOT NULL DEFAULT 0,
                criado_em   TEXT NOT NULL,
                encerrado_em TEXT
            );

            CREATE TABLE IF NOT EXISTS presencas (
                id              TEXT PRIMARY KEY,
                treinamento_id  TEXT NOT NULL REFERENCES treinamentos(id) ON DELETE CASCADE,
                nome            TEXT NOT NULL,
                cpf             TEXT NOT NULL,
                email           TEXT NOT NULL,
                cargo           TEXT,
                matricula       TEXT,
                registrado_em   TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_presencas_treinamento
                ON presencas(treinamento_id);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_presenca_cpf_unico
                ON presencas(treinamento_id, cpf);
        """)


def _init_postgres():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS treinamentos (
                id           TEXT PRIMARY KEY,
                nome         TEXT NOT NULL,
                data         DATE,
                hora         TIME,
                local        TEXT,
                setor        TEXT NOT NULL,
                instrutor    TEXT,
                descricao    TEXT,
                carga_horas  NUMERIC(5,1),
                encerrado    BOOLEAN NOT NULL DEFAULT FALSE,
                criado_em    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                encerrado_em TIMESTAMPTZ
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS presencas (
                id             TEXT PRIMARY KEY,
                treinamento_id TEXT NOT NULL REFERENCES treinamentos(id) ON DELETE CASCADE,
                nome           TEXT NOT NULL,
                cpf            TEXT NOT NULL,
                email          TEXT NOT NULL,
                cargo          TEXT,
                matricula      TEXT,
                registrado_em  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (treinamento_id, cpf)
            );
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_presencas_treinamento
                ON presencas(treinamento_id);
        """)


# ═══════════════════════════════════════════════════════════════════
# QUERIES — TREINAMENTOS
# ═══════════════════════════════════════════════════════════════════

def listar_treinamentos() -> list[dict]:
    with get_conn() as conn:
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute("""
                SELECT t.*, COUNT(p.id) AS total_presencas
                FROM treinamentos t
                LEFT JOIN presencas p ON p.treinamento_id = t.id
                GROUP BY t.id
                ORDER BY t.criado_em DESC
            """)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            cur = conn.execute("""
                SELECT t.*, COUNT(p.id) AS total_presencas
                FROM treinamentos t
                LEFT JOIN presencas p ON p.treinamento_id = t.id
                GROUP BY t.id
                ORDER BY t.criado_em DESC
            """)
            return [dict(row) for row in cur.fetchall()]


def buscar_treinamento(tid: str) -> Optional[dict]:
    with get_conn() as conn:
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute("SELECT * FROM treinamentos WHERE id = %s", (tid,))
            row = cur.fetchone()
            if not row:
                return None
            return dict(zip([d[0] for d in cur.description], row))
        else:
            cur = conn.execute("SELECT * FROM treinamentos WHERE id = ?", (tid,))
            row = cur.fetchone()
            return dict(row) if row else None


def criar_treinamento(dados: dict) -> str:
    import uuid
    tid = uuid.uuid4().hex[:12]
    agora = datetime.now().isoformat()

    with get_conn() as conn:
        sql = f"""
            INSERT INTO treinamentos
                (id, nome, data, hora, local, setor, instrutor, descricao, carga_horas, criado_em)
            VALUES ({ph(9)}, {p()})
        """
        params = (
            tid,
            dados["nome"],
            dados.get("data"),
            dados.get("hora"),
            dados.get("local"),
            dados["setor"],
            dados.get("instrutor"),
            dados.get("descricao"),
            dados.get("carga_horas"),
            agora,
        )
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(sql, params)
        else:
            conn.execute(sql, params)
    return tid


def encerrar_treinamento(tid: str):
    agora = datetime.now().isoformat()
    with get_conn() as conn:
        sql = f"UPDATE treinamentos SET encerrado = {1 if DB_TYPE == 'sqlite' else 'TRUE'}, encerrado_em = {p()} WHERE id = {p()}"
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(sql, (agora, tid))
        else:
            conn.execute(sql, (agora, tid))


def excluir_treinamento(tid: str):
    with get_conn() as conn:
        sql = f"DELETE FROM treinamentos WHERE id = {p()}"
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(sql, (tid,))
        else:
            conn.execute(sql, (tid,))


# ═══════════════════════════════════════════════════════════════════
# QUERIES — PRESENÇAS
# ═══════════════════════════════════════════════════════════════════

def listar_presencas(tid: str) -> list[dict]:
    with get_conn() as conn:
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM presencas WHERE treinamento_id = %s ORDER BY registrado_em",
                (tid,),
            )
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]
        else:
            cur = conn.execute(
                "SELECT * FROM presencas WHERE treinamento_id = ? ORDER BY registrado_em",
                (tid,),
            )
            return [dict(row) for row in cur.fetchall()]


def cpf_ja_registrado(tid: str, cpf: str) -> bool:
    cpf_limpo = "".join(filter(str.isdigit, cpf))
    with get_conn() as conn:
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM presencas WHERE treinamento_id = %s AND REGEXP_REPLACE(cpf, '[^0-9]', '', 'g') = %s",
                (tid, cpf_limpo),
            )
            return cur.fetchone() is not None
        else:
            cur = conn.execute(
                "SELECT 1 FROM presencas WHERE treinamento_id = ? AND REPLACE(REPLACE(REPLACE(cpf,'.',''),'-',''),' ','') = ?",
                (tid, cpf_limpo),
            )
            return cur.fetchone() is not None


def registrar_presenca(tid: str, dados: dict) -> tuple[bool, str]:
    """Registra presença. Retorna (sucesso, mensagem)."""
    import uuid

    # Verifica treinamento
    t = buscar_treinamento(tid)
    if not t:
        return False, "Treinamento não encontrado."

    enc = t["encerrado"]
    if enc == 1 or enc is True:
        return False, "Este treinamento está encerrado."

    # Verifica duplicata
    if cpf_ja_registrado(tid, dados["cpf"]):
        return False, "Este CPF já possui presença registrada neste treinamento."

    pid = uuid.uuid4().hex[:12]
    agora = datetime.now().isoformat()

    try:
        with get_conn() as conn:
            sql = f"""
                INSERT INTO presencas
                    (id, treinamento_id, nome, cpf, email, cargo, matricula, registrado_em)
                VALUES ({ph(8)})
            """
            params = (
                pid, tid,
                dados["nome"], dados["cpf"], dados["email"],
                dados.get("cargo"), dados.get("matricula"),
                agora,
            )
            if DB_TYPE == "postgres":
                cur = conn.cursor()
                cur.execute(sql, params)
            else:
                conn.execute(sql, params)
        return True, pid
    except Exception as e:
        if "UNIQUE" in str(e).upper():
            return False, "Este CPF já possui presença registrada neste treinamento."
        return False, f"Erro ao registrar: {e}"


def atualizar_treinamento(tid: str, dados: dict):
    """Atualiza os campos editáveis de um treinamento (não altera status/presenças)."""
    with get_conn() as conn:
        sql = f"""
            UPDATE treinamentos SET
                nome        = {p()},
                data        = {p()},
                hora        = {p()},
                local       = {p()},
                setor       = {p()},
                instrutor   = {p()},
                descricao   = {p()},
                carga_horas = {p()}
            WHERE id = {p()}
        """
        params = (
            dados["nome"],
            dados.get("data"),
            dados.get("hora"),
            dados.get("local"),
            dados["setor"],
            dados.get("instrutor"),
            dados.get("descricao"),
            dados.get("carga_horas"),
            tid,
        )
        if DB_TYPE == "postgres":
            cur = conn.cursor()
            cur.execute(sql, params)
        else:
            conn.execute(sql, params)
