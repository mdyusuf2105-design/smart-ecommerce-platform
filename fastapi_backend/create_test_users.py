from app.database.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


db = SessionLocal()

users = [
    {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin@12345",
        "role": "admin"
    },
    {
        "name": "Staff User",
        "email": "staff@example.com",
        "password": "Staff@12345",
        "role": "staff"
    },
    {
        "name": "Customer User",
        "email": "customer@example.com",
        "password": "Customer@12345",
        "role": "customer"
    }
]


for data in users:

    user = db.query(User).filter(
        User.email == data["email"]
    ).first()

    if user:
        user.name = data["name"]
        user.password = hash_password(data["password"])
        user.role = data["role"]
    else:
        user = User(
            name=data["name"],
            email=data["email"],
            password=hash_password(data["password"]),
            role=data["role"]
        )

        db.add(user)


db.commit()

print("Users created/reset successfully")

for data in users:
    print(
        data["email"],
        "|",
        data["password"],
        "|",
        data["role"]
    )

db.close()