from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'thesis_agent.db'}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
    from app.models import entities

    _prepare_lightweight_schema_migrations()
    Base.metadata.create_all(bind=engine)


def _prepare_lightweight_schema_migrations() -> None:
    """MVP 阶段轻量兼容旧 SQLite：必要时重建结构变化较大的规则表。"""

    with engine.begin() as conn:
        rule_columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(rule_memory)").fetchall()]
        if rule_columns and "rule_code" not in rule_columns:
            conn.exec_driver_sql("DROP TABLE rule_memory")
        project_columns = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(thesis_project)").fetchall()]
        if project_columns and "applied_template_rules" not in project_columns:
            conn.exec_driver_sql("ALTER TABLE thesis_project ADD COLUMN applied_template_rules JSON DEFAULT '{}'")

        llm_cols = [row[1] for row in conn.exec_driver_sql("PRAGMA table_info(llm_providers)").fetchall()]
        if llm_cols:
            add_cols = {
                "credential_source": "TEXT DEFAULT 'encrypted_database'",
                "credential_env_name": "TEXT DEFAULT ''",
                "api_key_ciphertext": "TEXT DEFAULT ''",
                "api_key_last_four": "TEXT DEFAULT ''",
                "encryption_version": "TEXT DEFAULT 'fernet_v1'",
                "credential_status": "TEXT DEFAULT 'missing'",
            }
            for c,t in add_cols.items():
                if c not in llm_cols:
                    conn.exec_driver_sql(f"ALTER TABLE llm_providers ADD COLUMN {c} {t}")

