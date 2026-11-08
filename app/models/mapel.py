from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MataPelajaran(Base):
    __tablename__ = "mata_pelajaran"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, nullable=False)
    deskripsi = Column(Text)
    guru_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    guru = relationship("User", back_populates="mapel_diajar")
    materi_list = relationship("Materi", back_populates="mapel", cascade="all, delete-orphan")
    kuis_list = relationship("Kuis", back_populates="mapel", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="mapel", cascade="all, delete-orphan")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    siswa_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mapel_id = Column(Integer, ForeignKey("mata_pelajaran.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    siswa = relationship("User", back_populates="enrollments", foreign_keys=[siswa_id])
    mapel = relationship("MataPelajaran", back_populates="enrollments")
