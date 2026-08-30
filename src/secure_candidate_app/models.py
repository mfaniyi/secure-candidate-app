from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320),unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    role: Mapped[str] = mapped_column((String(50)),nullable=False,default="user")


class Vacancy(Base):
    __tablename__ = "vacancies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200),nullable=False)
    description: Mapped[str] = mapped_column(Text,nullable=False)
    applicantsapp: Mapped[list["Applicant"]] = relationship(back_populates="vacancyrec")


class Applicant(Base):
    __tablename__ = "applicants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200),nullable=False)
    email: Mapped[str] = mapped_column(String(320),nullable=False)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"),nullable=False)
    vacancyrec: Mapped["Vacancy"] = relationship(back_populates="applicantsapp")
