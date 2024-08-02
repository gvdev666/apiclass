from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from database import get_database_connection

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    # Agrega aquí la URL de tu frontend, por ejemplo:
    "https://8d10-2806-2f0-1001-3046-e594-df43-6db0-bf5d.ngrok-free.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las orígenes. Ajusta según sea necesario.
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

class User(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserResponse)
async def create_user(user: User):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "INSERT INTO users (name, email) VALUES (%s, %s)"
        values = (user.name, user.email)
        cursor.execute(query, values)
        connection.commit()
        
        # Obtener el último ID insertado
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchone()[0]
        
        # Obtener el nuevo usuario insertado
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (last_id,))
        new_user = cursor.fetchone()
        
        return UserResponse(id=new_user[0], name=new_user[1], email=new_user[2])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.get("/users", response_model=List[UserResponse])
async def read_users():
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT id, name, email FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        return [UserResponse(id=user[0], name=user[1], email=user[2]) for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al recuperar usuarios.")
    finally:
        cursor.close()
        connection.close()

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT id, name, email FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(id=user[0], name=user[1], email=user[2])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: User):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE users SET name = %s, email = %s WHERE id = %s"
        values = (user.name, user.email, user_id)
        cursor.execute(query, values)
        connection.commit()
        
        # Obtener el usuario actualizado
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        updated_user = cursor.fetchone()
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(id=updated_user[0], name=updated_user[1], email=updated_user[2])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.delete("/users/{user_id}", response_model=dict)
async def delete_user(user_id: int):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "DELETE FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        connection.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        connection.close()
