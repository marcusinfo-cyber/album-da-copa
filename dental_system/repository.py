import sqlite3
from typing import List, Optional

from . import models


class PacienteJaExisteError(Exception):
    pass


class DentistaJaExisteError(Exception):
    pass


class RegistroNaoEncontradoError(Exception):
    pass


class DentalRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------- Pacientes ----------
    def cadastrar_paciente(self, paciente: models.Paciente) -> models.Paciente:
        try:
            cursor = self.conn.execute(
                "INSERT INTO pacientes (nome, cpf, data_nascimento, telefone, email, endereco) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (paciente.nome, paciente.cpf, paciente.data_nascimento,
                 paciente.telefone, paciente.email, paciente.endereco),
            )
        except sqlite3.IntegrityError as exc:
            raise PacienteJaExisteError(f"CPF {paciente.cpf} já cadastrado") from exc
        self.conn.commit()
        paciente.id = cursor.lastrowid
        return paciente

    def listar_pacientes(self) -> List[models.Paciente]:
        rows = self.conn.execute("SELECT * FROM pacientes ORDER BY nome").fetchall()
        return [self._row_to_paciente(r) for r in rows]

    def buscar_paciente(self, paciente_id: int) -> models.Paciente:
        row = self.conn.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()
        if row is None:
            raise RegistroNaoEncontradoError(f"Paciente {paciente_id} não encontrado")
        return self._row_to_paciente(row)

    def buscar_pacientes_por_nome(self, termo: str) -> List[models.Paciente]:
        rows = self.conn.execute(
            "SELECT * FROM pacientes WHERE nome LIKE ? ORDER BY nome", (f"%{termo}%",)
        ).fetchall()
        return [self._row_to_paciente(r) for r in rows]

    def atualizar_paciente(self, paciente: models.Paciente) -> None:
        if paciente.id is None:
            raise ValueError("Paciente sem id não pode ser atualizado")
        self.conn.execute(
            "UPDATE pacientes SET nome=?, cpf=?, data_nascimento=?, telefone=?, email=?, endereco=? "
            "WHERE id=?",
            (paciente.nome, paciente.cpf, paciente.data_nascimento, paciente.telefone,
             paciente.email, paciente.endereco, paciente.id),
        )
        self.conn.commit()

    def remover_paciente(self, paciente_id: int) -> None:
        self.conn.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        self.conn.commit()

    @staticmethod
    def _row_to_paciente(row: sqlite3.Row) -> models.Paciente:
        return models.Paciente(
            id=row["id"], nome=row["nome"], cpf=row["cpf"],
            data_nascimento=row["data_nascimento"], telefone=row["telefone"] or "",
            email=row["email"] or "", endereco=row["endereco"] or "",
        )

    # ---------- Dentistas ----------
    def cadastrar_dentista(self, dentista: models.Dentista) -> models.Dentista:
        try:
            cursor = self.conn.execute(
                "INSERT INTO dentistas (nome, cro, especialidade) VALUES (?, ?, ?)",
                (dentista.nome, dentista.cro, dentista.especialidade),
            )
        except sqlite3.IntegrityError as exc:
            raise DentistaJaExisteError(f"CRO {dentista.cro} já cadastrado") from exc
        self.conn.commit()
        dentista.id = cursor.lastrowid
        return dentista

    def listar_dentistas(self) -> List[models.Dentista]:
        rows = self.conn.execute("SELECT * FROM dentistas ORDER BY nome").fetchall()
        return [self._row_to_dentista(r) for r in rows]

    def buscar_dentista(self, dentista_id: int) -> models.Dentista:
        row = self.conn.execute("SELECT * FROM dentistas WHERE id = ?", (dentista_id,)).fetchone()
        if row is None:
            raise RegistroNaoEncontradoError(f"Dentista {dentista_id} não encontrado")
        return self._row_to_dentista(row)

    @staticmethod
    def _row_to_dentista(row: sqlite3.Row) -> models.Dentista:
        return models.Dentista(
            id=row["id"], nome=row["nome"], cro=row["cro"], especialidade=row["especialidade"] or "",
        )

    # ---------- Consultas ----------
    def agendar_consulta(self, consulta: models.Consulta) -> models.Consulta:
        self.buscar_paciente(consulta.paciente_id)
        self.buscar_dentista(consulta.dentista_id)
        cursor = self.conn.execute(
            "INSERT INTO consultas (paciente_id, dentista_id, data_hora, status, observacoes) "
            "VALUES (?, ?, ?, ?, ?)",
            (consulta.paciente_id, consulta.dentista_id, consulta.data_hora,
             consulta.status, consulta.observacoes),
        )
        self.conn.commit()
        consulta.id = cursor.lastrowid
        return consulta

    def listar_consultas(self, status: Optional[str] = None) -> List[models.Consulta]:
        if status:
            rows = self.conn.execute(
                "SELECT * FROM consultas WHERE status = ? ORDER BY data_hora", (status,)
            ).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM consultas ORDER BY data_hora").fetchall()
        return [self._row_to_consulta(r) for r in rows]

    def atualizar_status_consulta(self, consulta_id: int, status: str) -> None:
        cursor = self.conn.execute("UPDATE consultas SET status=? WHERE id=?", (status, consulta_id))
        if cursor.rowcount == 0:
            raise RegistroNaoEncontradoError(f"Consulta {consulta_id} não encontrada")
        self.conn.commit()

    def cancelar_consulta(self, consulta_id: int) -> None:
        self.atualizar_status_consulta(consulta_id, "cancelada")

    @staticmethod
    def _row_to_consulta(row: sqlite3.Row) -> models.Consulta:
        return models.Consulta(
            id=row["id"], paciente_id=row["paciente_id"], dentista_id=row["dentista_id"],
            data_hora=row["data_hora"], status=row["status"], observacoes=row["observacoes"] or "",
        )

    # ---------- Tratamentos ----------
    def registrar_tratamento(self, tratamento: models.Tratamento) -> models.Tratamento:
        self.buscar_paciente(tratamento.paciente_id)
        self.buscar_dentista(tratamento.dentista_id)
        cursor = self.conn.execute(
            "INSERT INTO tratamentos "
            "(paciente_id, dentista_id, consulta_id, data, dente, procedimento, descricao, valor, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (tratamento.paciente_id, tratamento.dentista_id, tratamento.consulta_id, tratamento.data,
             tratamento.dente, tratamento.procedimento, tratamento.descricao,
             tratamento.valor, tratamento.status),
        )
        self.conn.commit()
        tratamento.id = cursor.lastrowid
        return tratamento

    def historico_paciente(self, paciente_id: int) -> List[models.Tratamento]:
        rows = self.conn.execute(
            "SELECT * FROM tratamentos WHERE paciente_id = ? ORDER BY data", (paciente_id,)
        ).fetchall()
        return [self._row_to_tratamento(r) for r in rows]

    def atualizar_status_tratamento(self, tratamento_id: int, status: str) -> None:
        cursor = self.conn.execute("UPDATE tratamentos SET status=? WHERE id=?", (status, tratamento_id))
        if cursor.rowcount == 0:
            raise RegistroNaoEncontradoError(f"Tratamento {tratamento_id} não encontrado")
        self.conn.commit()

    @staticmethod
    def _row_to_tratamento(row: sqlite3.Row) -> models.Tratamento:
        return models.Tratamento(
            id=row["id"], paciente_id=row["paciente_id"], dentista_id=row["dentista_id"],
            consulta_id=row["consulta_id"], data=row["data"], dente=row["dente"] or "",
            procedimento=row["procedimento"], descricao=row["descricao"] or "",
            valor=row["valor"], status=row["status"],
        )
