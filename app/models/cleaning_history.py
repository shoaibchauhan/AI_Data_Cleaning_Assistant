from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class CleaningHistory(Base):
    __tablename__ = "cleaning_history"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("file_uploads.id"), nullable=True)  
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    cleaned_file_path = Column(String, nullable=True)  
    cleaning_steps = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


    user = relationship("User", back_populates="cleaning_history")
    file = relationship("FileUpload", back_populates="history")