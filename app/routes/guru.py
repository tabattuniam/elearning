from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os, shutil
from app.database import get_db
from app.models.mapel import MataPelajaran, Enrollment
from app.models.materi import Materi
from app.models.kuis import Kuis, Soal, PilihanJawaban, HasilKuis
from app.models.user import User
from app.auth import require_guru

router = APIRouter(prefix="/guru")
templates = Jinja2Templates(directory="app/templates")
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    mapel_list = db.query(MataPelajaran).filter(MataPelajaran.guru_id == user.id).all()
    return templates.TemplateResponse("guru/dashboard.html", {
        "request": request, "user": user, "mapel_list": mapel_list
    })

# --- MATA PELAJARAN ---
@router.get("/mapel/tambah", response_class=HTMLResponse)
async def tambah_mapel_form(request: Request, user=Depends(require_guru)):
    return templates.TemplateResponse("guru/mapel_form.html", {
        "request": request, "user": user, "edit": None
    })

@router.post("/mapel/tambah")
async def tambah_mapel(
    request: Request,
    nama: str = Form(...),
    deskripsi: str = Form(""),
    user=Depends(require_guru),
    db: Session = Depends(get_db)
):
    mapel = MataPelajaran(nama=nama, deskripsi=deskripsi, guru_id=user.id)
    db.add(mapel)
    db.commit()
    return RedirectResponse(url="/guru", status_code=302)

@router.get("/mapel/{mapel_id}", response_class=HTMLResponse)
async def detail_mapel(mapel_id: int, request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if not mapel:
        raise HTTPException(status_code=404)
    enrollments = db.query(Enrollment).filter(Enrollment.mapel_id == mapel_id).all()
    return templates.TemplateResponse("guru/mapel_detail.html", {
        "request": request, "user": user, "mapel": mapel, "enrollments": enrollments
    })

@router.get("/mapel/{mapel_id}/hapus")
async def hapus_mapel(mapel_id: int, user=Depends(require_guru), db: Session = Depends(get_db)):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if mapel:
        db.delete(mapel)
        db.commit()
    return RedirectResponse(url="/guru", status_code=302)

# --- MATERI ---
@router.get("/mapel/{mapel_id}/materi/tambah", response_class=HTMLResponse)
async def tambah_materi_form(mapel_id: int, request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if not mapel:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("guru/materi_form.html", {
        "request": request, "user": user, "mapel": mapel, "edit": None
    })

@router.post("/mapel/{mapel_id}/materi/tambah")
async def tambah_materi(
    mapel_id: int,
    request: Request,
    judul: str = Form(...),
    konten: str = Form(""),
    urutan: int = Form(0),
    file: UploadFile = File(None),
    user=Depends(require_guru),
    db: Session = Depends(get_db)
):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if not mapel:
        raise HTTPException(status_code=404)
    file_path = None
    if file and file.filename:
        dest = os.path.join(UPLOAD_DIR, file.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_path = f"/static/uploads/{file.filename}"
    materi = Materi(judul=judul, konten=konten, urutan=urutan, file_path=file_path, mapel_id=mapel_id)
    db.add(materi)
    db.commit()
    return RedirectResponse(url=f"/guru/mapel/{mapel_id}", status_code=302)

@router.get("/mapel/{mapel_id}/materi/{materi_id}/hapus")
async def hapus_materi(mapel_id: int, materi_id: int, user=Depends(require_guru), db: Session = Depends(get_db)):
    materi = db.query(Materi).filter(Materi.id == materi_id, Materi.mapel_id == mapel_id).first()
    if materi:
        db.delete(materi)
        db.commit()
    return RedirectResponse(url=f"/guru/mapel/{mapel_id}", status_code=302)

# --- KUIS ---
@router.get("/mapel/{mapel_id}/kuis/tambah", response_class=HTMLResponse)
async def tambah_kuis_form(mapel_id: int, request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if not mapel:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("guru/kuis_form.html", {
        "request": request, "user": user, "mapel": mapel
    })

@router.post("/mapel/{mapel_id}/kuis/tambah")
async def tambah_kuis(
    mapel_id: int,
    request: Request,
    judul: str = Form(...),
    deskripsi: str = Form(""),
    user=Depends(require_guru),
    db: Session = Depends(get_db)
):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    if not mapel:
        raise HTTPException(status_code=404)
    kuis = Kuis(judul=judul, deskripsi=deskripsi, mapel_id=mapel_id)
    db.add(kuis)
    db.commit()
    return RedirectResponse(url=f"/guru/kuis/{kuis.id}/soal", status_code=302)

@router.get("/kuis/{kuis_id}/soal", response_class=HTMLResponse)
async def kelola_soal(kuis_id: int, request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    kuis = db.query(Kuis).join(MataPelajaran).filter(Kuis.id == kuis_id, MataPelajaran.guru_id == user.id).first()
    if not kuis:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("guru/kuis_soal.html", {
        "request": request, "user": user, "kuis": kuis
    })

@router.post("/kuis/{kuis_id}/soal/tambah")
async def tambah_soal(
    kuis_id: int,
    request: Request,
    pertanyaan: str = Form(...),
    pilihan_a: str = Form(...),
    pilihan_b: str = Form(...),
    pilihan_c: str = Form(...),
    pilihan_d: str = Form(...),
    jawaban_benar: str = Form(...),
    user=Depends(require_guru),
    db: Session = Depends(get_db)
):
    kuis = db.query(Kuis).join(MataPelajaran).filter(Kuis.id == kuis_id, MataPelajaran.guru_id == user.id).first()
    if not kuis:
        raise HTTPException(status_code=404)
    soal = Soal(pertanyaan=pertanyaan, kuis_id=kuis_id, urutan=len(kuis.soal_list) + 1)
    db.add(soal)
    db.flush()
    for huruf, teks in [("A", pilihan_a), ("B", pilihan_b), ("C", pilihan_c), ("D", pilihan_d)]:
        pilihan = PilihanJawaban(teks=teks, adalah_benar=(huruf == jawaban_benar), soal_id=soal.id)
        db.add(pilihan)
    db.commit()
    return RedirectResponse(url=f"/guru/kuis/{kuis_id}/soal", status_code=302)

@router.get("/kuis/{kuis_id}/hasil", response_class=HTMLResponse)
async def lihat_hasil(kuis_id: int, request: Request, user=Depends(require_guru), db: Session = Depends(get_db)):
    kuis = db.query(Kuis).join(MataPelajaran).filter(Kuis.id == kuis_id, MataPelajaran.guru_id == user.id).first()
    if not kuis:
        raise HTTPException(status_code=404)
    hasil_list = db.query(HasilKuis).filter(HasilKuis.kuis_id == kuis_id).all()
    return templates.TemplateResponse("guru/kuis_hasil.html", {
        "request": request, "user": user, "kuis": kuis, "hasil_list": hasil_list
    })

# --- ENROLLMENT ---
@router.post("/mapel/{mapel_id}/enroll")
async def enroll_siswa(
    mapel_id: int,
    username_siswa: str = Form(...),
    user=Depends(require_guru),
    db: Session = Depends(get_db)
):
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id, MataPelajaran.guru_id == user.id).first()
    siswa = db.query(User).filter(User.username == username_siswa, User.role == "siswa").first()
    if mapel and siswa:
        exists = db.query(Enrollment).filter(Enrollment.siswa_id == siswa.id, Enrollment.mapel_id == mapel_id).first()
        if not exists:
            db.add(Enrollment(siswa_id=siswa.id, mapel_id=mapel_id))
            db.commit()
    return RedirectResponse(url=f"/guru/mapel/{mapel_id}", status_code=302)
