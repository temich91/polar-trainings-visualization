from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import DeclarativeBase


# SQLAlchemy base class for models
class Base(DeclarativeBase): pass


class Account(Base):
    """
    Stores credentials for later scraping and accessing saved session data.
    Passwords are stored only as hashes.

    Attributes:
        id: Primary key identifier.
        name: Username displayed in the application.
        login: Polar Flow account login/email.
        password_hash: Securely hashed password.
    """

    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    login = Column(String)
    password_hash = Column(String)


class Summary(Base):
    """
    Stores summary information about users' sessions.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to account.
        session_id: Polar Flow session identifier.
        start_datetime: Session start datetime in `YYYY-MM-DDTHH:MM:SS` format.
        duration: Total duration in seconds.
        distance: Distance traveled in meters.
        hr_avg: Average heart rate in bpm.
        pace_avg: Average pace in sec/km.
        pace_max: Maximum pace in sec/km.
        ascent: Elevation gain in meters.
        descent: Elevation loss in meters.
        calories: Calories burned in kcal.
        cadence_avg: Average cadence in pairs of steps/min.
    """

    __tablename__ = "summary"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    session_id = Column(Integer)
    start_datetime = Column(Text)
    duration = Column(Integer)
    distance = Column(Float)
    hr_avg = Column(Integer)
    pace_avg = Column(Integer)
    pace_max = Column(Integer)
    ascent = Column(Integer)
    descent = Column(Integer)
    calories = Column(Integer)
    cadence_avg = Column(Integer)


class Telemetry(Base):
    """
    Stores per-second telemetry data from training sessions.

    Attributes:
        id: Primary key identifier.
        user_id: Foreign key to account.
        session_id: Polar Flow session identifier.
        time: Seconds elapsed since session start.
        hr: Heart rate in bpm.
        pace: Pace in sec/km.
        cadence: Cadence in pairs of steps/min.
        altitude: Elevation in meters above sea level.
    """

    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts.id"))
    session_id = Column(Integer)
    time = Column(Integer)
    hr = Column(Integer)
    pace = Column(Integer)
    cadence = Column(Integer)
    altitude = Column(Integer)
