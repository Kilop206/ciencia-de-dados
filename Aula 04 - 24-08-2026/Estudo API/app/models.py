from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Colaborador(Base):
    __tablename__ = "colaborators"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    matricula: Mapped[str] = mapped_column(String(100))
    setor: Mapped[str] = mapped_column(String(255))
    cargo: Mapped[str] = mapped_column(String(255))