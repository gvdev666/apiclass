from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from database import get_database_connection

app = FastAPI()

class User(BaseModel):
    name: str
    email: str

@app.post("/users")
async def create_user(user: User):
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO users (name, email) VALUES (%s, %s)"
    values = (user.name, user.email)
    cursor.execute(query, values)
    connection.commit()
    connection.close()
    return {"message": "User created successfully"}

@app.get("/users")
async def read_users():
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    connection.close()
    return users