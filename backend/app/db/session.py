from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    from app.modules.assets.models import Asset
    from app.modules.liabilities.models import Liability
    from app.modules.transactions.models import CachedTransaction
    from app.modules.goals.models import Goal
    Base.metadata.create_all(bind=engine)
