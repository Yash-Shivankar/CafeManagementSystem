from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """One session per request. It does not commit.

    It deliberately does not `yield db` and then `db.commit()`, and no
    data-access class commits inside create, update or delete either. Two
    problems with doing it that way:

    1. **No unit of work.** A use-case that wrote three rows and failed on the
       fourth had already committed the first three, with no way to undo them.
    2. **The commit ran after the response.** FastAPI tears a yield-dependency
       down *after* the handler returns, so a commit that failed there raised
       against a client who had already been told 200 OK.

    Services now own the transaction and commit at the end of a use-case, where
    a failure can still turn into an error response. This function's only jobs
    are to hand out a session, roll back anything left open if the request
    exploded, and close.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        if db.in_transaction():
            db.rollback()
        db.close()
