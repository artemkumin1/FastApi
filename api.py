
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg

app = FastAPI()

DATABASE_URL = "postgresql://postgres:291511@localhost:5432/postgres"

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

class User(BaseModel):
    name: str
    email: str

class User_id(BaseModel):
    user_id: int

class UserUpdate(BaseModel):
    name: Optional[str]=None
    email: Optional[str]=None

@app.post("/users/")
async def create_user(user: User):
    conn = await get_db_connection()
    try:
        await conn.execute("INSERT INTO users (name, email) VALUES ($1, $2)",user.name, user.email)
        return {"message": "User created successfully"}
    finally:
        await conn.close()

@app.get("/users/")
async def get_users():
    conn = await get_db_connection()
    try:
        users = await conn.fetch("SELECT * FROM users")
        return [{"id": user["id"], "name": user["name"], "email": user["email"]} for user in users]
    finally:
        await conn.close()

@app.delete("/users/")
async def delete_user(user_id: User_id ):
    conn=await get_db_connection()
    try:
        if (await conn.execute ("DELETE FROM users WHERE id = $1", user_id.user_id))=="DELETE 0":
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "deleted successfully"}
    finally:
        await conn.close()

@app.put("/users/")
async def update_user(user_id: User_id, user_update: UserUpdate):
    conn = await get_db_connection()
    try:
        existing_user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id.user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_update.name is not None:
            await conn.execute("UPDATE users SET name = $1 WHERE id = $2", user_update.name, user_id.user_id)

        if user_update.email is not None:
            await conn.execute("UPDATE users SET email = $1 WHERE id = $2", user_update.email, user_id.user_id)
        return {"message": "User updated successfully"}
    finally:
        await conn.close()

