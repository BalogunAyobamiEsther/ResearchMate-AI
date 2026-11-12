
from sqlalchemy import inspect, text

from backend.app.core.database import Base, engine
from backend.app.models.conversation import Conversation, Message


def init_db():
    """
    Create registered database tables and apply safe database migrations.

    Existing conversations and messages are preserved.
    """

    # Create tables that do not already exist.
    Base.metadata.create_all(bind=engine)

    # Apply migrations to existing SQLite databases.
    if engine.dialect.name == "sqlite":
        table_name = Conversation.__tablename__

        with engine.begin() as connection:
            inspector = inspect(connection)

            if inspector.has_table(table_name):
                columns = {
                    column["name"]
                    for column in inspector.get_columns(table_name)
                }

                # Add ownership column without deleting existing records.
                if "owner_session_id" not in columns:
                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            "ADD COLUMN owner_session_id VARCHAR(64)"
                        )
                    )

                # Create an index for efficient session-based queries.
                quoted_table = (
                    connection.dialect.identifier_preparer.quote(table_name)
                )

                connection.execute(
                    text(
                        f"CREATE INDEX IF NOT EXISTS "
                        f"ix_{table_name}_owner_session_id "
                        f"ON {quoted_table} (owner_session_id)"
                    )
                )


if __name__ == "__main__":
    init_db()
    print("Research History database initialized successfully.")
