from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Kuis(Base):
    __tablename__ = "kuis"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, nullable=False)
    deskripsi = Column(Text)
    mapel_id = Column(Integer, ForeignKey("mata_pelajaran.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    mapel = relationship("MataPelajaran", back_populates="kuis_list")
    soal_list = relationship("Soal", back_populates="kuis", cascade="all, delete-orphan")
    hasil_list = relationship("HasilKuis", back_populates="kuis", cascade="all, delete-orphan")

class Soal(Base):
    __tablename__ = "soal"

    id = Column(Integer, primary_key=True, index=True)
    pertanyaan = Column(Text, nullable=False)
    urutan = Column(Integer, default=0)
    kuis_id = Column(Integer, ForeignKey("kuis.id"), nullable=False)

    kuis = relationship("Kuis", back_populates="soal_list")
    pilihan = relationship("PilihanJawaban", back_populates="soal", cascade="all, delete-orphan")

class PilihanJawaban(Base):
    __tablename__ = "pilihan_jawaban"

    id = Column(Integer, primary_key=True, index=True)
    teks = Column(String, nullable=False)
    adalah_benar = Column(Boolean, default=False)
    soal_id = Column(Integer, ForeignKey("soal.id"), nullable=False)

    soal = relationship("Soal", back_populates="pilihan")

class HasilKuis(Base):
    __tablename__ = "hasil_kuis"

    id = Column(Integer, primary_key=True, index=True)
    siswa_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    kuis_id = Column(Integer, ForeignKey("kuis.id"), nullable=False)
    nilai = Column(Float, default=0)
    dikerjakan_at = Column(DateTime, default=datetime.utcnow)

    siswa = relationship("User", back_populates="hasil_kuis")
    kuis = relationship("Kuis", back_populates="hasil_list")
