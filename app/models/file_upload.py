from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=True)  
    file_path = Column(String, nullable=True)  
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  

    
    user = relationship("User", back_populates="uploads")
    history = relationship("CleaningHistory", back_populates="file")