from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.models import *
from app.routes import auth, admin, guru, siswa
from app.auth import hash_password
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-Learning SMK")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(guru.router)
app.include_router(siswa.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

def seed_admin():
    db = Session(bind=engine)
    from app.models.user import User, RoleEnum
    if not db.query(User).filter(User.username == "admin").first():
        admin_user = User(
            nama="Administrator",
            username="admin",
            password_hash=hash_password("admin123"),
            role=RoleEnum.admin
        )
        db.add(admin_user)
        db.commit()
    db.close()

seed_admin()
