from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User, Wish
from config import DATABASE_URL, DB_ECHO
from typing import Optional, List, Tuple

engine = create_engine(DATABASE_URL, echo=DB_ECHO)

SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Database Initialization - Creating All Tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


def get_db() -> Session:
    """Getting a database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


# === Functions for working with users ===


def get_or_create_user(
    user_id: int, username: str = None, first_name: str = None
) -> User:
    """Get a user or create a new user"""
    db = get_db()
    try:
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            user = User(user_id=user_id, username=username, first_name=first_name)
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"A new user created: {user_id}")

        return user
    finally:
        db.close()


def get_user(user_id: int) -> Optional[User]:
    """Get user by id"""
    db = get_db()
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    finally:
        db.close()


# === Functions for working with wishes ===


def add_wish(
    user_id: int,
    title: str,
    description: str = None,
    url: str = None,
    price: str = None,
    image_file_id: str = None,
) -> Wish:
    """Add a new wish"""
    db = get_db()
    try:
        wish = Wish(
            user_id=user_id,
            title=title,
            description=description,
            url=url,
            price=price,
            image_file_id=image_file_id,
        )
        db.add(wish)
        db.commit()
        db.refresh(wish)
        print(f"✅ A wish added: {title} for user {user_id}")
        return wish
    finally:
        db.close()


def get_user_wishes(user_id: int) -> List[Wish]:
    """Get all user`s wishes"""
    db = get_db()
    try:
        wishes = (
            db.query(Wish)
            .filter(Wish.user_id == user_id)
            .order_by(Wish.created_at.desc())
            .all()
        )
        return wishes
    finally:
        db.close()


def get_wish(wish_id: int) -> Optional[Wish]:
    """Get a wish by id"""
    db = get_db()
    try:
        return db.query(Wish).filter(Wish.wish_id == wish_id).first()
    finally:
        db.close()


def delete_wish(wish_id: int, user_id: int) -> bool:
    """Delete a wish (only if it belongs to the user)"""
    db = get_db()
    try:
        wish = (
            db.query(Wish)
            .filter(Wish.wish_id == wish_id, Wish.user_id == user_id)
            .first()
        )
        if wish:
            db.delete(wish)
            db.commit()
            print(f"A wish deleted: {wish_id}")
            return True
        return False
    finally:
        db.close()


def update_wish(wish_id: int, user_id: int, **kwargs) -> Optional[Wish]:
    """Update the wish"""
    db = get_db()
    try:
        wish = (
            db.query(Wish)
            .filter(Wish.wish_id == wish_id, Wish.user_id == user_id)
            .first()
        )
        if wish:
            for key, value in kwargs.items():
                if hasattr(wish, key) and value is not None:
                    setattr(wish, key, value)
            db.commit()
            db.refresh(wish)
            print(f"The wish updated: {wish_id}")
            return wish
        return None
    finally:
        db.close()
