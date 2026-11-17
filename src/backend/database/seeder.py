import os
import sys
from pathlib import Path

from core.security import get_password_hash
from database.models import User, UserRole
from database.session import SessionLocal
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))

load_dotenv()

admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")


def seed_admin():
    if not admin_password:
        print("Error: ADMIN_PASSWORD is not set in .env")
        return

    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if not existing:
            hashed = get_password_hash(admin_password)

            admin = User(
                username=admin_username,
                password_hash=hashed,
                role=UserRole.Admin,
            )
            db.add(admin)
            db.commit()
            print("admin created succesfully")
        else:
            print("admin already exists")
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
