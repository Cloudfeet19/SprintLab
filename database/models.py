from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Date, ForeignKey, UniqueConstraint
from datetime import date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class AthleteTable(db.Model):
    __tablename__ = "athlete"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    gender: Mapped[str] = mapped_column(String(250), nullable=False)
    # grade: Mapped[int] = mapped_column(Integer, nullable=False)
    athlete_class: Mapped[int] = mapped_column(Integer, nullable=False)

    results = db.relationship("ResultTable", back_populates="athlete") # Create the parent / child relationship


class ResultTable(db.Model):
    __tablename__ = "result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    athlete_id: Mapped[int] = mapped_column(Integer, ForeignKey("athlete.id"))
    athlete = db.relationship("AthleteTable", back_populates="results") # Create the parent / child relationship
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
