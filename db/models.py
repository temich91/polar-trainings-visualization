from sqlalchemy import Column, ForeignKey, Integer, String, Text, Real
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase): pass

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    login = Column(String)
    password_hash = Column(String)

class Summary(Base):
    __tablename__ = "summary"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    training_id = Column(Integer)
    start_datetime = Column(Text)
    duration = Column(Integer)
    distance = Column(Real)
    hr_avg = Column(Integer)
    pace_avg = Column(Integer)
    pace_max = Column(Integer)
    ascent = Column(Integer)
    descent = Column(Integer)
    calories = Column(Integer)
    cadence_avg = Column(Integer)

class Telemetry(Base):
    __tablename__ = "telemetry"
    user_id = Column(Integer, ForeignKey("accounts.id"))
    training_id = Column(Integer)
    timestamp = Column(Integer)
    hr = Column(Integer)
    pace = Column(Integer)
    cadence = Column(Integer)
    altitude = Column(Integer)
