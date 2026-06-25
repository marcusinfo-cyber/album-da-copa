import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "dental_system.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    data_nascimento TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    endereco TEXT
);

CREATE TABLE IF NOT EXISTS dentistas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    cro TEXT UNIQUE NOT NULL,
    especialidade TEXT
);

CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    dentista_id INTEGER NOT NULL REFERENCES dentistas(id) ON DELETE CASCADE,
    data_hora TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'agendada',
    observacoes TEXT
);

CREATE TABLE IF NOT EXISTS tratamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE CASCADE,
    dentista_id INTEGER NOT NULL REFERENCES dentistas(id) ON DELETE CASCADE,
    consulta_id INTEGER REFERENCES consultas(id) ON DELETE SET NULL,
    data TEXT NOT NULL,
    dente TEXT,
    procedimento TEXT NOT NULL,
    descricao TEXT,
    valor REAL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pendente'
);
"""


def conectar(db_path=None):
    path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar(conn):
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.commit()
