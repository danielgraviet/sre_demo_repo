from app.db import SessionLocal, engine
from app.models import Base, UserProfile

_SEED_DATA = [
    {
        "id": i,
        "username": f"user{i:02d}",
        "email": f"user{i:02d}@example.com",
        "bio": f"Bio for user {i:02d}",
    }
    for i in range(1, 11)
]


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted = 0
        for data in _SEED_DATA:
            exists = db.query(UserProfile).filter(UserProfile.id == data["id"]).first()
            if not exists:
                db.add(UserProfile(**data))
                inserted += 1
        db.commit()
        print(f"Seed complete: {inserted} rows inserted, {len(_SEED_DATA) - inserted} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
