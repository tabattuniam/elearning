from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.auth import require_admin, hash_password

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(require_admin), db: Session = Depends(get_db)):
    total_guru = db.query(User).filter(User.role == "guru").count()
    total_siswa = db.query(User).filter(User.role == "siswa").count()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "user": user,
        "total_guru": total_guru, "total_siswa": total_siswa
    })

@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, user=Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).filter(User.role != "admin").order_by(User.role, User.nama).all()
    return templates.TemplateResponse("admin/users.html", {
        "request": request, "user": user, "users": users
    })

@router.get("/users/tambah", response_class=HTMLResponse)
async def tambah_user_form(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse("admin/user_form.html", {
        "request": request, "user": user, "edit": None, "error": None
    })

@router.post("/users/tambah")
async def tambah_user(
    request: Request,
    nama: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        return templates.TemplateResponse("admin/user_form.html", {
            "request": request, "user": user, "edit": None,
            "error": "Username sudah dipakai"
        })
    new_user = User(nama=nama, username=username, password_hash=hash_password(password), role=role)
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)

@router.get("/users/{uid}/hapus")
async def hapus_user(uid: int, user=Depends(require_admin), db: Session = Depends(get_db)):
    target = db.query(User).filter(User.id == uid).first()
    if target and target.role != "admin":
        db.delete(target)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)
