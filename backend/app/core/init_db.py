from backend.app.core.database import Base, engine
from backend.app.models.conversation import Conversation, Message


def init_db():
    """
    Create all registered database tables.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Research History database tables created successfully.")