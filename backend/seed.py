from app import models, database, auth
from sqlalchemy.orm import Session

db = database.SessionLocal()

def create_super_admin():
    # Check if superadmin exists
    super_admin = db.query(models.User).filter(models.User.email == "admin@bina.com").first()
    if not super_admin:
        print("Creating Super Admin...")
        hashed_password = auth.get_password_hash("admin123")
        user = models.User(
            email="admin@bina.com",
            hashed_password=hashed_password,
            role=0, # SuperAdmin
            is_active=1
        )
        db.add(user)
        db.commit()
        print("Super Admin created: admin@bina.com / admin123")
    else:
        print("Super Admin already exists.")

if __name__ == "__main__":
    # Create tables if not exist (migrations are better but this works for dev)
    models.Base.metadata.create_all(bind=database.engine)
    create_super_admin()
