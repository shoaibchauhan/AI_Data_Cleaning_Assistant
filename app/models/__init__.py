# app/models/__init__.py

from app.database import Base  # This is crucial
from .user import User
from .file_upload import FileUpload
from .cleaning_history import CleaningHistory
