from dataclasses import dataclass
from typing import Optional


@dataclass
class Paciente:
    nome: str
    cpf: str
    data_nascimento: str
    telefone: str = ""
    email: str = ""
    endereco: str = ""
    id: Optional[int] = None


@dataclass
class Dentista:
    nome: str
    cro: str
    especialidade: str = ""
    id: Optional[int] = None


@dataclass
class Consulta:
    paciente_id: int
    dentista_id: int
    data_hora: str
    status: str = "agendada"
    observacoes: str = ""
    id: Optional[int] = None


@dataclass
class Tratamento:
    paciente_id: int
    dentista_id: int
    data: str
    procedimento: str
    dente: str = ""
    descricao: str = ""
    valor: float = 0.0
    status: str = "pendente"
    consulta_id: Optional[int] = None
    id: Optional[int] = None
