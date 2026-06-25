import sqlite3
import unittest

from dental_system import models
from dental_system.database import inicializar
from dental_system.repository import (
    DentalRepository,
    DentistaJaExisteError,
    PacienteJaExisteError,
    RegistroNaoEncontradoError,
)


class RepositoryTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        inicializar(self.conn)
        self.repo = DentalRepository(self.conn)

    def tearDown(self):
        self.conn.close()

    def _criar_paciente(self, cpf="11111111111"):
        return self.repo.cadastrar_paciente(
            models.Paciente(nome="Ana Silva", cpf=cpf, data_nascimento="01/01/1990")
        )

    def _criar_dentista(self, cro="CRO123"):
        return self.repo.cadastrar_dentista(models.Dentista(nome="Dr. João", cro=cro))

    def test_cadastrar_e_listar_paciente(self):
        paciente = self._criar_paciente()
        self.assertIsNotNone(paciente.id)
        pacientes = self.repo.listar_pacientes()
        self.assertEqual(len(pacientes), 1)
        self.assertEqual(pacientes[0].nome, "Ana Silva")

    def test_cpf_duplicado_gera_erro(self):
        self._criar_paciente()
        with self.assertRaises(PacienteJaExisteError):
            self._criar_paciente()

    def test_cro_duplicado_gera_erro(self):
        self._criar_dentista()
        with self.assertRaises(DentistaJaExisteError):
            self._criar_dentista()

    def test_buscar_paciente_inexistente(self):
        with self.assertRaises(RegistroNaoEncontradoError):
            self.repo.buscar_paciente(999)

    def test_buscar_pacientes_por_nome(self):
        self._criar_paciente()
        encontrados = self.repo.buscar_pacientes_por_nome("ana")
        self.assertEqual(len(encontrados), 1)
        self.assertEqual(self.repo.buscar_pacientes_por_nome("inexistente"), [])

    def test_atualizar_paciente(self):
        paciente = self._criar_paciente()
        paciente.telefone = "99999-0000"
        self.repo.atualizar_paciente(paciente)
        atualizado = self.repo.buscar_paciente(paciente.id)
        self.assertEqual(atualizado.telefone, "99999-0000")

    def test_agendar_consulta_e_concluir(self):
        paciente = self._criar_paciente()
        dentista = self._criar_dentista()
        consulta = self.repo.agendar_consulta(
            models.Consulta(paciente_id=paciente.id, dentista_id=dentista.id,
                             data_hora="10/03/2026 14:00")
        )
        self.repo.atualizar_status_consulta(consulta.id, "concluida")
        self.assertEqual(len(self.repo.listar_consultas("concluida")), 1)
        self.assertEqual(len(self.repo.listar_consultas("agendada")), 0)

    def test_agendar_consulta_paciente_inexistente(self):
        dentista = self._criar_dentista()
        with self.assertRaises(RegistroNaoEncontradoError):
            self.repo.agendar_consulta(
                models.Consulta(paciente_id=999, dentista_id=dentista.id, data_hora="10/03/2026 14:00")
            )

    def test_cancelar_consulta_inexistente(self):
        with self.assertRaises(RegistroNaoEncontradoError):
            self.repo.cancelar_consulta(999)

    def test_registrar_tratamento_e_historico(self):
        paciente = self._criar_paciente()
        dentista = self._criar_dentista()
        self.repo.registrar_tratamento(
            models.Tratamento(paciente_id=paciente.id, dentista_id=dentista.id, data="10/03/2026",
                               procedimento="Limpeza", dente="11", valor=150.0)
        )
        historico = self.repo.historico_paciente(paciente.id)
        self.assertEqual(len(historico), 1)
        self.assertEqual(historico[0].procedimento, "Limpeza")
        self.assertEqual(historico[0].status, "pendente")

    def test_atualizar_status_tratamento(self):
        paciente = self._criar_paciente()
        dentista = self._criar_dentista()
        tratamento = self.repo.registrar_tratamento(
            models.Tratamento(paciente_id=paciente.id, dentista_id=dentista.id, data="10/03/2026",
                               procedimento="Limpeza", valor=150.0)
        )
        self.repo.atualizar_status_tratamento(tratamento.id, "concluido")
        historico = self.repo.historico_paciente(paciente.id)
        self.assertEqual(historico[0].status, "concluido")

    def test_remover_paciente_remove_dados_associados(self):
        paciente = self._criar_paciente()
        dentista = self._criar_dentista()
        self.repo.agendar_consulta(
            models.Consulta(paciente_id=paciente.id, dentista_id=dentista.id,
                             data_hora="10/03/2026 14:00")
        )
        self.repo.registrar_tratamento(
            models.Tratamento(paciente_id=paciente.id, dentista_id=dentista.id, data="10/03/2026",
                               procedimento="Limpeza")
        )
        self.repo.remover_paciente(paciente.id)
        self.assertEqual(self.repo.listar_consultas(), [])
        self.assertEqual(self.repo.historico_paciente(paciente.id), [])


if __name__ == "__main__":
    unittest.main()
