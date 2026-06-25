from datetime import datetime

from . import models
from .database import conectar, inicializar
from .repository import (
    DentalRepository,
    DentistaJaExisteError,
    PacienteJaExisteError,
    RegistroNaoEncontradoError,
)


def ler_data(prompt: str, formato: str = "%d/%m/%Y") -> str:
    while True:
        valor = input(prompt).strip()
        try:
            datetime.strptime(valor, formato)
            return valor
        except ValueError:
            print(f"Data inválida. Use o formato {formato}.")


def ler_data_hora(prompt: str, formato: str = "%d/%m/%Y %H:%M") -> str:
    while True:
        valor = input(prompt).strip()
        try:
            datetime.strptime(valor, formato)
            return valor
        except ValueError:
            print(f"Data/hora inválida. Use o formato {formato}.")


def ler_inteiro(prompt: str) -> int:
    while True:
        valor = input(prompt).strip()
        if valor.isdigit():
            return int(valor)
        print("Digite um número válido.")


def ler_float(prompt: str, padrao: float = 0.0) -> float:
    valor = input(prompt).strip().replace(",", ".")
    if not valor:
        return padrao
    try:
        return float(valor)
    except ValueError:
        print("Valor inválido, usando 0.0")
        return padrao


class DentalCLI:
    def __init__(self, repo: DentalRepository):
        self.repo = repo

    def executar(self) -> None:
        acoes = {
            "1": self.menu_pacientes,
            "2": self.menu_dentistas,
            "3": self.menu_consultas,
            "4": self.menu_tratamentos,
            "5": self.menu_relatorios,
        }
        while True:
            print("\n=== Sistema Odontológico ===")
            print("1. Pacientes")
            print("2. Dentistas")
            print("3. Consultas")
            print("4. Tratamentos / Histórico")
            print("5. Relatórios")
            print("0. Sair")
            escolha = input("Escolha uma opção: ").strip()
            if escolha == "0":
                print("Até logo!")
                return
            acao = acoes.get(escolha)
            if acao:
                acao()
            else:
                print("Opção inválida.")

    # ---------- Pacientes ----------
    def menu_pacientes(self) -> None:
        while True:
            print("\n-- Pacientes --")
            print("1. Cadastrar")
            print("2. Listar")
            print("3. Buscar por nome")
            print("4. Editar")
            print("5. Remover")
            print("0. Voltar")
            escolha = input("Escolha: ").strip()
            if escolha == "0":
                return
            elif escolha == "1":
                self._cadastrar_paciente()
            elif escolha == "2":
                self._listar_pacientes()
            elif escolha == "3":
                termo = input("Nome a buscar: ").strip()
                self._listar_pacientes(self.repo.buscar_pacientes_por_nome(termo))
            elif escolha == "4":
                self._editar_paciente()
            elif escolha == "5":
                self._remover_paciente()
            else:
                print("Opção inválida.")

    def _cadastrar_paciente(self) -> None:
        nome = input("Nome: ").strip()
        cpf = input("CPF (somente números): ").strip()
        nascimento = ler_data("Data de nascimento (dd/mm/aaaa): ")
        telefone = input("Telefone: ").strip()
        email = input("Email: ").strip()
        endereco = input("Endereço: ").strip()
        paciente = models.Paciente(nome=nome, cpf=cpf, data_nascimento=nascimento,
                                    telefone=telefone, email=email, endereco=endereco)
        try:
            paciente = self.repo.cadastrar_paciente(paciente)
            print(f"Paciente cadastrado com id {paciente.id}.")
        except PacienteJaExisteError as exc:
            print(f"Erro: {exc}")

    def _listar_pacientes(self, pacientes=None) -> None:
        pacientes = pacientes if pacientes is not None else self.repo.listar_pacientes()
        if not pacientes:
            print("Nenhum paciente encontrado.")
            return
        for p in pacientes:
            print(f"[{p.id}] {p.nome} - CPF {p.cpf} - Nasc. {p.data_nascimento} - Tel {p.telefone}")

    def _editar_paciente(self) -> None:
        paciente_id = ler_inteiro("Id do paciente: ")
        try:
            paciente = self.repo.buscar_paciente(paciente_id)
        except RegistroNaoEncontradoError as exc:
            print(f"Erro: {exc}")
            return
        print(f"Editando {paciente.nome} (deixe vazio para manter o valor atual)")
        paciente.nome = input(f"Nome [{paciente.nome}]: ").strip() or paciente.nome
        paciente.telefone = input(f"Telefone [{paciente.telefone}]: ").strip() or paciente.telefone
        paciente.email = input(f"Email [{paciente.email}]: ").strip() or paciente.email
        paciente.endereco = input(f"Endereço [{paciente.endereco}]: ").strip() or paciente.endereco
        self.repo.atualizar_paciente(paciente)
        print("Paciente atualizado.")

    def _remover_paciente(self) -> None:
        paciente_id = ler_inteiro("Id do paciente: ")
        confirmacao = input(
            "Confirma remoção? Isso também remove consultas e tratamentos do paciente (s/n): "
        ).strip().lower()
        if confirmacao == "s":
            self.repo.remover_paciente(paciente_id)
            print("Paciente removido.")

    # ---------- Dentistas ----------
    def menu_dentistas(self) -> None:
        while True:
            print("\n-- Dentistas --")
            print("1. Cadastrar")
            print("2. Listar")
            print("0. Voltar")
            escolha = input("Escolha: ").strip()
            if escolha == "0":
                return
            elif escolha == "1":
                self._cadastrar_dentista()
            elif escolha == "2":
                self._listar_dentistas()
            else:
                print("Opção inválida.")

    def _cadastrar_dentista(self) -> None:
        nome = input("Nome: ").strip()
        cro = input("CRO: ").strip()
        especialidade = input("Especialidade: ").strip()
        try:
            dentista = self.repo.cadastrar_dentista(
                models.Dentista(nome=nome, cro=cro, especialidade=especialidade)
            )
            print(f"Dentista cadastrado com id {dentista.id}.")
        except DentistaJaExisteError as exc:
            print(f"Erro: {exc}")

    def _listar_dentistas(self) -> None:
        dentistas = self.repo.listar_dentistas()
        if not dentistas:
            print("Nenhum dentista cadastrado.")
            return
        for d in dentistas:
            print(f"[{d.id}] {d.nome} - CRO {d.cro} - {d.especialidade}")

    # ---------- Consultas ----------
    def menu_consultas(self) -> None:
        while True:
            print("\n-- Consultas --")
            print("1. Agendar")
            print("2. Listar todas")
            print("3. Listar por status")
            print("4. Concluir")
            print("5. Cancelar")
            print("0. Voltar")
            escolha = input("Escolha: ").strip()
            if escolha == "0":
                return
            elif escolha == "1":
                self._agendar_consulta()
            elif escolha == "2":
                self._listar_consultas(self.repo.listar_consultas())
            elif escolha == "3":
                status = input("Status (agendada/concluida/cancelada): ").strip()
                self._listar_consultas(self.repo.listar_consultas(status))
            elif escolha == "4":
                consulta_id = ler_inteiro("Id da consulta: ")
                try:
                    self.repo.atualizar_status_consulta(consulta_id, "concluida")
                    print("Consulta concluída.")
                except RegistroNaoEncontradoError as exc:
                    print(f"Erro: {exc}")
            elif escolha == "5":
                consulta_id = ler_inteiro("Id da consulta: ")
                try:
                    self.repo.cancelar_consulta(consulta_id)
                    print("Consulta cancelada.")
                except RegistroNaoEncontradoError as exc:
                    print(f"Erro: {exc}")
            else:
                print("Opção inválida.")

    def _agendar_consulta(self) -> None:
        paciente_id = ler_inteiro("Id do paciente: ")
        dentista_id = ler_inteiro("Id do dentista: ")
        data_hora = ler_data_hora("Data e hora (dd/mm/aaaa hh:mm): ")
        observacoes = input("Observações: ").strip()
        try:
            consulta = self.repo.agendar_consulta(
                models.Consulta(paciente_id=paciente_id, dentista_id=dentista_id,
                                 data_hora=data_hora, observacoes=observacoes)
            )
            print(f"Consulta agendada com id {consulta.id}.")
        except RegistroNaoEncontradoError as exc:
            print(f"Erro: {exc}")

    def _listar_consultas(self, consultas) -> None:
        if not consultas:
            print("Nenhuma consulta encontrada.")
            return
        for c in consultas:
            print(f"[{c.id}] {c.data_hora} - Paciente {c.paciente_id} - Dentista {c.dentista_id} - {c.status}")

    # ---------- Tratamentos ----------
    def menu_tratamentos(self) -> None:
        while True:
            print("\n-- Tratamentos --")
            print("1. Registrar")
            print("2. Histórico de um paciente")
            print("3. Atualizar status")
            print("0. Voltar")
            escolha = input("Escolha: ").strip()
            if escolha == "0":
                return
            elif escolha == "1":
                self._registrar_tratamento()
            elif escolha == "2":
                paciente_id = ler_inteiro("Id do paciente: ")
                self._exibir_historico(paciente_id)
            elif escolha == "3":
                tratamento_id = ler_inteiro("Id do tratamento: ")
                status = input("Novo status (pendente/concluido/cancelado): ").strip()
                try:
                    self.repo.atualizar_status_tratamento(tratamento_id, status)
                    print("Status atualizado.")
                except RegistroNaoEncontradoError as exc:
                    print(f"Erro: {exc}")
            else:
                print("Opção inválida.")

    def _registrar_tratamento(self) -> None:
        paciente_id = ler_inteiro("Id do paciente: ")
        dentista_id = ler_inteiro("Id do dentista: ")
        data = ler_data("Data do tratamento (dd/mm/aaaa): ")
        dente = input("Dente (número FDI, opcional): ").strip()
        procedimento = input("Procedimento: ").strip()
        descricao = input("Descrição: ").strip()
        valor = ler_float("Valor (R$): ")
        try:
            tratamento = self.repo.registrar_tratamento(
                models.Tratamento(paciente_id=paciente_id, dentista_id=dentista_id, data=data,
                                   dente=dente, procedimento=procedimento, descricao=descricao,
                                   valor=valor)
            )
            print(f"Tratamento registrado com id {tratamento.id}.")
        except RegistroNaoEncontradoError as exc:
            print(f"Erro: {exc}")

    def _exibir_historico(self, paciente_id: int) -> None:
        try:
            paciente = self.repo.buscar_paciente(paciente_id)
        except RegistroNaoEncontradoError as exc:
            print(f"Erro: {exc}")
            return
        historico = self.repo.historico_paciente(paciente_id)
        print(f"\nHistórico de {paciente.nome}:")
        if not historico:
            print("Nenhum tratamento registrado.")
            return
        for t in historico:
            dente_info = f" (dente {t.dente})" if t.dente else ""
            print(f"[{t.id}] {t.data} - {t.procedimento}{dente_info} - R$ {t.valor:.2f} - {t.status}")

    # ---------- Relatórios ----------
    def menu_relatorios(self) -> None:
        print("\n-- Relatórios --")
        pacientes = self.repo.listar_pacientes()
        consultas_agendadas = self.repo.listar_consultas("agendada")
        print(f"Total de pacientes: {len(pacientes)}")
        print(f"Total de dentistas: {len(self.repo.listar_dentistas())}")
        print(f"Consultas agendadas: {len(consultas_agendadas)}")
        total_recebido = sum(
            t.valor
            for p in pacientes
            for t in self.repo.historico_paciente(p.id)
            if t.status == "concluido"
        )
        print(f"Total recebido (tratamentos concluídos): R$ {total_recebido:.2f}")


def main() -> None:
    conn = conectar()
    inicializar(conn)
    repo = DentalRepository(conn)
    cli = DentalCLI(repo)
    try:
        cli.executar()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
