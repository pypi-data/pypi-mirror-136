"""Moduł obsługujący bazę danych przechowującą tablicę wyników."""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def add_score(nick: str, score: int):
    """Dodanie wyniku gracza do tablicy wyników.

    Args:
        nick (str): Nick gracza.
        score (int): Liczba punktów uzyskanych przez gracza.
    """
    s = Score()
    s.nick = nick
    s.score = score
    session.add(s)
    session.commit()


class Score(Base):
    """Tablica w bazie danych przechowująca rekordy postaci ```nick - wynik```."""
    __tablename__ = 'Scoreboard'
    id = Column(Integer, primary_key=True) #: Id rekordu.
    nick = Column(String(20), nullable=False) #: Nazwa gracza.
    score = Column(Integer, nullable=False) #: Wynik gracza.


engine = create_engine('sqlite:///scoreboard.db', echo=False) #: Utworzenie bazy danych.
Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session() #: Utworzenie sesji dla zapisu i odczytu tablicy.
