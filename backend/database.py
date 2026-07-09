import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, Column, String, Text, Integer, DateTime, JSON, Boolean, text, func
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from config import CONFIG

DATABASE_URL = CONFIG.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./autoagent.db"

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    title = Column(String(255), nullable=True)
    pinned = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False, default="")
    tool_calls = Column(Text, nullable=True)
    tool_call_id = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)

# Migration: add pinned column to existing sessions table
try:
    from sqlalchemy import inspect as _insp
    _inspector = _insp(engine)
    _cols = [c["name"] for c in _inspector.get_columns("sessions")]
    if "pinned" not in _cols:
        with engine.connect() as conn:
            if "sqlite" in DATABASE_URL:
                conn.execute(text("ALTER TABLE sessions ADD COLUMN pinned BOOLEAN DEFAULT 0"))
            else:
                conn.execute(text("ALTER TABLE sessions ADD COLUMN pinned BOOLEAN DEFAULT FALSE"))
            conn.commit()
except Exception:
    pass


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync() -> Session:
    return SessionLocal()


def create_session(db: Session, session_id: str, title: Optional[str] = None) -> SessionDB:
    now = datetime.now(timezone.utc)
    session = SessionDB(id=session_id, title=title, created_at=now, updated_at=now)
    db.add(session)
    db.commit()
    return session


def get_session(db: Session, session_id: str) -> Optional[SessionDB]:
    return db.query(SessionDB).filter(SessionDB.id == session_id).first()


def get_all_sessions(db: Session) -> list[SessionDB]:
    return db.query(SessionDB).order_by(func.coalesce(SessionDB.pinned, False).desc(), SessionDB.updated_at.desc()).all()


def delete_session(db: Session, session_id: str) -> bool:
    sess = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if not sess:
        return False
    db.query(MessageDB).filter(MessageDB.session_id == session_id).delete()
    db.delete(sess)
    db.commit()
    return True


def update_session_title(db: Session, session_id: str, title: str) -> Optional[SessionDB]:
    sess = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if not sess:
        return None
    sess.title = title
    sess.updated_at = datetime.now(timezone.utc)
    db.commit()
    return sess


def touch_session(db: Session, session_id: str) -> None:
    sess = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if sess:
        sess.updated_at = datetime.now(timezone.utc)
        db.commit()


def toggle_pin_session(db: Session, session_id: str) -> Optional[SessionDB]:
    sess = db.query(SessionDB).filter(SessionDB.id == session_id).first()
    if not sess:
        return None
    sess.pinned = not sess.pinned
    sess.updated_at = datetime.now(timezone.utc)
    db.commit()
    return sess


def add_message(
    db: Session,
    session_id: str,
    role: str,
    content: str = "",
    tool_calls: Optional[list] = None,
    tool_call_id: Optional[str] = None,
) -> MessageDB:
    msg = MessageDB(
        session_id=session_id,
        role=role,
        content=content,
        tool_calls=json.dumps(tool_calls) if tool_calls else None,
        tool_call_id=tool_call_id,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(msg)
    db.commit()
    return msg


def get_messages(db: Session, session_id: str) -> list[MessageDB]:
    return db.query(MessageDB).filter(MessageDB.session_id == session_id).order_by(MessageDB.id).all()
