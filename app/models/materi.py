from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Materi(Base):
    __tablename__ = "materi"

    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, nullable=False)
    konten = Column(Text)
    file_path = Column(String)
    urutan = Column(Integer, default=0)
    mapel_id = Column(Integer, ForeignKey("mata_pelajaran.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    mapel = relationship("MataPelajaran", back_populates="materi_list")
