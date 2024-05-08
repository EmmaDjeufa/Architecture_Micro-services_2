from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List

app = FastAPI()

# Configuration de la base de données (utilisez vos propres informations de connexion)
DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle pour stocker les informations utilisateur
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

# Créez la table dans la base de données
Base.metadata.create_all(bind=engine)

# Sécurité HTTP Basic
security = HTTPBasic()

# Fonction de vérification de l'authentification
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = SessionLocal().query(User).filter_by(username=credentials.username).first()
    if not user or user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# Route pour créer un compte utilisateur
@app.post("/user/signup")
def create_user(username: str, password: str):
    db = SessionLocal()
    db_user = User(username=username, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# Routes protégées par authentification
@app.get("/user/whoami")
def get_user_info(user: User = Depends(authenticate_user)):
    return {"username": user.username, "password_hashed": user.password}

@app.put("/files/{filename}")
def upload_file(filename: str, user: User = Depends(authenticate_user)):
    # Implémentez la logique pour stocker le fichier dans le système de fichiers de l'utilisateur
    return {"message": f"File {filename} uploaded successfully"}

@app.delete("/files/{filename}")
def delete_file(filename: str, user: User = Depends(authenticate_user)):
    # Implémentez la logique pour supprimer le fichier associé au nom de fichier fourni
    return {"message": f"File {filename} deleted successfully"}

@app.get("/files/{filename}")
def get_file(filename: str, user: User = Depends(authenticate_user)):
    # Implémentez la logique pour récupérer le contenu du fichier
    return {"message": f"File {filename} retrieved successfully"}

@app.get("/files/{prefix}")
def get_files_by_prefix(prefix: str, user: User = Depends(authenticate_user)):
    # Implémentez la logique pour récupérer la liste des chemins vers les fichiers sous le préfixe donné
    return {"message": f"Files under prefix {prefix} retrieved successfully"}

# Route pour se renommer
@app.post("/user/rename")
def rename_user(new_username: str, user: User = Depends(authenticate_user)):
    user.username = new_username
    SessionLocal().commit()
    return {"message": "User renamed successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
