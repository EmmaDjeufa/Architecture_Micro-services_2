from fastapi import FastAPI, Depends, HTTPException, UploadFile, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import aiofiles
import os

app = FastAPI()

# Chemin absolu vers le répertoire frontend
frontend_directory = "/app/frontend"
if not os.path.isdir(frontend_directory):
    raise RuntimeError(f"Directory '{frontend_directory}' does not exist")

app.mount("/", StaticFiles(directory=frontend_directory, html=True), name="frontend")

# Configuration de la base de données (utilisez vos propres informations de connexion)
DATABASE_URL = "postgresql://EmmaDB:1234STORAge!@postgres/STORAgeDB"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour stocker les informations des utilisateurs
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

# Créer la table dans la base de données
Base.metadata.create_all(bind=engine)

# Sécurité HTTP Basic
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction de vérification de l'authentification
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=credentials.username).first()
    if not user or not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# Modèles Pydantic
class UserIn(BaseModel):
    username: str
    password: str

class UserRename(BaseModel):
    new_username: str

# Route pour créer un compte utilisateur
@app.post("user/signup")
def create_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = User(username=username, password=get_password_hash(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Inscription réussie"}

# Routes protégées par l'authentification
@app.get("/user/auth")
def get_user_info(user: User = Depends(authenticate_user)):
    return {"username": user.username, "password_hashed": user.password}

@app.put("/files/{filename}")
async def upload_file(filename: str, file: UploadFile, user: User = Depends(authenticate_user)):
    os.makedirs('./files', exist_ok=True)
    async with aiofiles.open(f'./files/{filename}', 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return {"message": f"File {filename} uploaded successfully"}

@app.delete("/files/{filename}")
def delete_file(filename: str, user: User = Depends(authenticate_user)):
    file_path = f'./files/{filename}'
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/files/{filename}")
async def get_file(filename: str, user: User = Depends(authenticate_user)):
    file_path = f'./files/{filename}'
    if os.path.exists(file_path):
        async with aiofiles.open(file_path, 'r') as in_file:
            content = await in_file.read()
        return {"message": f"File {filename} retrieved successfully", "content": content}
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/files/prefix/{prefix}")
def get_files_by_prefix(prefix: str, user: User = Depends(authenticate_user)):
    files = [f for f in os.listdir('./files') if f.startswith(prefix)]
    return {"message": f"Files under prefix {prefix} retrieved successfully", "files": files}

@app.get("/files")
def list_files(user: User = Depends(authenticate_user)):
    files = os.listdir('./files')
    return {"message": "Files retrieved successfully", "files": files}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
