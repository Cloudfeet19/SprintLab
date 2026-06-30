from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, ForeignKey, UniqueConstraint
from typing import List
from datetime import date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class UserTable(UserMixin, db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    results: Mapped[List["ResultTable"]] = relationship("ResultTable", back_populates="user")
    athletes: Mapped[List["AthleteTable"]] = relationship("AthleteTable", back_populates="user")

class AthleteTable(db.Model):
    __tablename__ = "athlete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    gender: Mapped[str] = mapped_column(String(250), nullable=False)
    athlete_class: Mapped[int] = mapped_column(Integer, nullable=False)

    # children below
    results: Mapped["ResultTable"] = relationship("ResultTable", back_populates="athlete") # Create the parent / child relationship

    # parents below
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    user: Mapped["UserTable"] = relationship("UserTable", back_populates="athletes")

class ResultTable(db.Model):
    __tablename__ = "result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # parents below
    athlete_id: Mapped[int] = mapped_column(Integer, ForeignKey("athlete.id"))
    athlete: Mapped["AthleteTable"] = relationship("AthleteTable", back_populates="results") # Create the parent / child relationship

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    user: Mapped["UserTable"] = relationship("UserTable", back_populates="results")

    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    event: Mapped[str] = mapped_column(String(250), nullable=False)
    raw_result: Mapped[str] = mapped_column(String(250), nullable=False)
    result_in_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    result_in_inches: Mapped[float] = mapped_column(Float, nullable=True)
    result_in_meters: Mapped[float] = mapped_column(Float, nullable=True)
    wind: Mapped[float] = mapped_column(Float, nullable=True)
    placement: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    season: Mapped[str] = mapped_column(String(250), nullable=False)
    meet: Mapped[str] = mapped_column(String(250), nullable=False)
    atmosphere: Mapped[str] = mapped_column(String(250), nullable=False)
    race_type: Mapped[str] = mapped_column(String(250), nullable=False)
    performance_type: Mapped[str] = mapped_column(String(250), nullable=False)
