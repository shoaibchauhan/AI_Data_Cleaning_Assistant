from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.file_upload import FileUpload
from app.models.user import User
import aiofiles
import os
import uuid
import csv

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "app/static/uploads"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only allow CSV files
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Generate unique file name
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # Save the file asynchronously
        async with aiofiles.open(file_location, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)

        # Process the CSV data (e.g., cleaning operations could be added here)
        with open(file_location, 'r') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                pass  # Add your row processing logic here

        # Save file metadata to DB
        new_file = FileUpload(
            original_filename=file.filename,  # Changed to match the column name in DB
            file_path=file_location,
            user_id=current_user.id
        )
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)

    except Exception as e:
        # Remove the file if error occurs
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    return {
        "id": new_file.id,
        "filename": new_file.original_filename,  # Changed to reflect DB column name
        "uploaded_at": new_file.uploaded_at,
        "message": "File uploaded and processed successfully"
    }

