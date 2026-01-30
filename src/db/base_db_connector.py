from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from models import Base
from abc import ABC


class BaseDBConnector(ABC):
    def __init__(self, db_path):
        self.db_url = f"sqlite:///{db_path}"
        self.engine = None
        self.session_factory = None
        self._initialize()

    def _initialize(self):
        self.engine = create_engine(self.db_url)
        self.session_factory = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self):
        if self.engine:
            self.engine.dispose()
