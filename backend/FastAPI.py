from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import UploadFile
import aiofiles
import os

class File(BaseModel):
    name: str
app = FastAPI()

# Mount the directory containing your HTML pages
app.mount("/", StaticFiles(directory="./frontend", html=True), name="frontend")

# Database configuration (use your own connection information)
DATABASE_URL = "postgresql://EmmaDB:1234STORAge!@postgres/StorAgeDB"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model to store user information
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

# Create the table in the database
Base.metadata.create_all(bind=engine)

# HTTP Basic Security
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

# Authentication verification function
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = SessionLocal().query(User).filter_by(username=credentials.username).first()
    if not user or not pwd_context.verify(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user

# Pydantic models
class UserIn(BaseModel):
    username: str
    password: str

class UserRename(BaseModel):
    new_username: str

# Route to create a user account
@app.post("/user/signup")
def create_user(user_in: UserIn):
    db = SessionLocal()
    db_user = User(username=user_in.username, password=get_password_hash(user_in.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

# Routes protected by authentication
@app.get("/user/auth")
def get_user_info(user: User = Depends(authenticate_user)):
    return {"username": user.username, "password_hashed": user.password}

@app.put("/files/{filename}")
async def upload_file(filename: str, file: UploadFile = File(...), user: User = Depends(authenticate_user)):
    async with aiofiles.open(f'./files/{filename}', 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write
    return {"message": f"File {filename} uploaded successfully"}

@app.delete("/files/{filename}")
def delete_file(filename: str, user: User = Depends(authenticate_user)):
    os.remove(f'./files/{filename}')
    return {"message": f"File {filename} deleted successfully"}

@app.get("/files/{filename}")
async def get_file(filename: str, user: User = Depends(authenticate_user)):
    async with aiofiles.open(f'./files/{filename}', 'r') as in_file:
        content = await in_file.read()
    return {"message": f"File {filename} retrieved successfully", "content": content}

@app.get("/files/{prefix}")
def get_files_by_prefix(prefix: str, user: User = Depends(authenticate_user)):
    files = [f for f in os.listdir('./files') if f.startswith(prefix)]
    return {"message": f"Files under prefix {prefix} retrieved successfully", "files": files}

# Route to rename
@app.get("/files")
def list_files(user: User = Depends(authenticate_user)):
    files = os.listdir('./files')
    return {"message": "Files retrieved successfully", "files": files}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)