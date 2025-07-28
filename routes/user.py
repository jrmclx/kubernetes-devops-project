from fastapi import APIRouter
from config.db import conn
from models.user import users
from schemas.user import User, UserCount
from typing import List
from starlette.status import HTTP_204_NO_CONTENT
from sqlalchemy import func, select

from cryptography.fernet import Fernet

user = APIRouter()
key = Fernet.generate_key()
f = Fernet(key)

@user.get("/")
def root():
    return {"message": "Welcome on on the Users management API"}
    
@user.get(
    "/users",
    tags=["users"],
    response_model=List[User],
    description="Get a list of all users",
)
def get_users():
    return conn.execute(users.select()).fetchall()


@user.get("/users/count", tags=["users"], response_model=UserCount)
def get_users_count():
    result = conn.execute(select([func.count()]).select_from(users))
    return {"total": tuple(result)[0][0]}


@user.get(
    "/users/{id}",
    tags=["users"],
    response_model=User,
    description="Get a single user by Id",
)
def get_user(id: str):
    return conn.execute(users.select().where(users.c.id == id)).first()


@user.post("/", tags=["users"], response_model=User, description="Create a new user")
def create_user(user: User):
    new_user = {"name": user.name, "email": user.email}
    new_user["password"] = f.encrypt(user.password.encode("utf-8"))

    # Insère et récupère l'ID
    result = conn.execute(users.insert().returning(users.c.id).values(new_user))
    user_id = result.fetchone()[0]
    print("Inserted user ID (via RETURNING):", user_id)

    # Renvoie l'utilisateur nouvellement inséré
    return conn.execute(users.select().where(users.c.id == user_id)).first()

@user.put(
    "/users/{id}", tags=["users"], response_model=User, description="Update a User by Id"
)
def update_user(user: User, id: int):
    conn.execute(
        users.update()
        .values(
            name=user.name,
            email=user.email,
            password=f.encrypt(user.password.encode("utf-8"))
            )
        .where(users.c.id == id)
    )
    return conn.execute(users.select().where(users.c.id == id)).first()


@user.delete("/{id}", tags=["users"], status_code=HTTP_204_NO_CONTENT)
def delete_user(id: int):
    conn.execute(users.delete().where(users.c.id == id))
    return conn.execute(users.select().where(users.c.id == id)).first()
