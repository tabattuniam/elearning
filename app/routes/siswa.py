from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.mapel import MataPelajaran, Enrollment
from app.models.materi import Materi
from app.models.kuis import Kuis, HasilKuis
from app.auth import require_login

router = APIRouter(prefix="/siswa")
templates = Jinja2Templates(directory="app/templates")

@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.siswa_id == user.id).all()
    return templates.TemplateResponse("siswa/dashboard.html", {
        "request": request, "user": user, "enrollments": enrollments
    })

@router.get("/mapel/{mapel_id}", response_class=HTMLResponse)
async def detail_mapel(mapel_id: int, request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.siswa_id == user.id, Enrollment.mapel_id == mapel_id).first()
    if not enrollment:
        raise HTTPException(status_code=403, detail="Anda tidak terdaftar di kelas ini")
    mapel = db.query(MataPelajaran).filter(MataPelajaran.id == mapel_id).first()
    hasil_ids = {h.kuis_id for h in db.query(HasilKuis).filter(HasilKuis.siswa_id == user.id).all()}
    return templates.TemplateResponse("siswa/mapel_detail.html", {
        "request": request, "user": user, "mapel": mapel, "hasil_ids": hasil_ids
    })

@router.get("/materi/{materi_id}", response_class=HTMLResponse)
async def baca_materi(materi_id: int, request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    materi = db.query(Materi).first()
    materi = db.query(Materi).filter(Materi.id == materi_id).first()
    if not materi:
        raise HTTPException(status_code=404)
    enrollment = db.query(Enrollment).filter(Enrollment.siswa_id == user.id, Enrollment.mapel_id == materi.mapel_id).first()
    if not enrollment:
        raise HTTPException(status_code=403)
    return templates.TemplateResponse("siswa/materi.html", {
        "request": request, "user": user, "materi": materi
    })

@router.get("/kuis/{kuis_id}", response_class=HTMLResponse)
async def kerjakan_kuis(kuis_id: int, request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    kuis = db.query(Kuis).filter(Kuis.id == kuis_id).first()
    if not kuis:
        raise HTTPException(status_code=404)
    enrollment = db.query(Enrollment).filter(Enrollment.siswa_id == user.id, Enrollment.mapel_id == kuis.mapel_id).first()
    if not enrollment:
        raise HTTPException(status_code=403)
    sudah = db.query(HasilKuis).filter(HasilKuis.siswa_id == user.id, HasilKuis.kuis_id == kuis_id).first()
    if sudah:
        return templates.TemplateResponse("siswa/kuis_hasil.html", {
            "request": request, "user": user, "kuis": kuis, "hasil": sudah
        })
    return templates.TemplateResponse("siswa/kuis.html", {
        "request": request, "user": user, "kuis": kuis
    })

@router.post("/kuis/{kuis_id}/submit")
async def submit_kuis(kuis_id: int, request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    kuis = db.query(Kuis).filter(Kuis.id == kuis_id).first()
    if not kuis:
        raise HTTPException(status_code=404)
    sudah = db.query(HasilKuis).filter(HasilKuis.siswa_id == user.id, HasilKuis.kuis_id == kuis_id).first()
    if sudah:
        return RedirectResponse(url=f"/siswa/kuis/{kuis_id}", status_code=302)
    form_data = await request.form()
    benar = 0
    total = len(kuis.soal_list)
    for soal in kuis.soal_list:
        jawaban_id = form_data.get(f"soal_{soal.id}")
        if jawaban_id:
            for pilihan in soal.pilihan:
                if str(pilihan.id) == jawaban_id and pilihan.adalah_benar:
                    benar += 1
    nilai = (benar / total * 100) if total > 0 else 0
    hasil = HasilKuis(siswa_id=user.id, kuis_id=kuis_id, nilai=nilai)
    db.add(hasil)
    db.commit()
    return RedirectResponse(url=f"/siswa/kuis/{kuis_id}", status_code=302)

@router.get("/nilai", response_class=HTMLResponse)
async def lihat_nilai(request: Request, user=Depends(require_login), db: Session = Depends(get_db)):
    hasil_list = db.query(HasilKuis).filter(HasilKuis.siswa_id == user.id).all()
    return templates.TemplateResponse("siswa/nilai.html", {
        "request": request, "user": user, "hasil_list": hasil_list
    })
