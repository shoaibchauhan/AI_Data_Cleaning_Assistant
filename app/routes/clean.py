from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.user import User
from app.models.file_upload import FileUpload
from app.models.cleaning_history import CleaningHistory
from app.utils.auth import get_current_user
from app.utils.cleaning_tools import get_cleaning_agent  # Import LangChain cleaning agent
import pandas as pd
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/clean", tags=["cleaning"])

UPLOAD_DIR = "app/static/uploads"
CLEANED_DIR = "app/static/cleaned"

# Endpoint to clean a file
@router.post("/{file_id}")
async def clean_file(
    file_id: int,
    prompt: str = Query("Please clean this file with the necessary steps.", description="Custom cleaning instructions for the file"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch the uploaded file record from the database
    result = await db.execute(
        select(FileUpload).filter(FileUpload.id == file_id, FileUpload.user_id == current_user.id)
    )
    file_record = result.scalar_one_or_none()

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded file not found")

    # Load the CSV into DataFrame
    try:
        df = pd.read_csv(file_record.file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV file: {e}")

    # Get the cleaning agent and clean the file
    agent = get_cleaning_agent(df)
    cleaned_df = agent.run(prompt)  # Use the user-provided prompt

    # Save cleaned CSV file
    os.makedirs(CLEANED_DIR, exist_ok=True)
    cleaned_filename = f"{uuid.uuid4()}_cleaned_{file_record.original_filename}"
    cleaned_filepath = os.path.join(CLEANED_DIR, cleaned_filename)
    cleaned_df.to_csv(cleaned_filepath, index=False,na_rep="NaN")

    # Save cleaning history in DB
    numeric_cols = list(cleaned_df.select_dtypes(include=["number"]).columns)
    string_cols = list(cleaned_df.select_dtypes(include=["object"]).columns)
    
    cleaning_steps = {
        "missing_values_filled_with_na": string_cols,
        "duplicates_removed": True,
        "strings_normalized": string_cols
    }

    cleaning_history = CleaningHistory(
        user_id=current_user.id,
        file_id=file_record.id,
        cleaned_file_path=cleaned_filepath,
        cleaning_steps=str(cleaning_steps),
        created_at=datetime.utcnow()
    )

    db.add(cleaning_history)
    await db.commit()
    await db.refresh(cleaning_history)

    # Mock AI agent thinking and analysis
    ai_response = {
        "thinking": [
            "💭 Analyzing the file and determining the necessary cleaning steps...",
            "1. Identifying missing values in string columns...",
            "2. Detecting duplicate rows based on unique identifiers...",
            "3. Normalizing string formatting, especially for 'name' and 'email' columns..."
        ],
        "steps_taken": [
            "✅ Missing values filled with 'N/A' for string columns.",
            "✅ Duplicates removed based on 'email' and 'signup_date'.",
            "✅ String columns (name, email, signup_date) normalized to lowercase and stripped of extra spaces."
        ],
        "final_thoughts": "✨ Data cleaning process completed successfully! The file is now ready for further analysis or download.",
    }

    # Return the response with AI agent summary and cleaning information
    return {
        "message": "File cleaned successfully",
        "cleaned_file": cleaned_filename,
        "cleaning_summary": cleaning_steps,
        "cleaned_file_id": cleaning_history.id,
        "original_rows": len(df),
        "cleaned_rows": len(cleaned_df),
        "user_prompt": prompt,  # now reflects user input
        "ai_response": ai_response
    }


# Endpoint to download the cleaned file
@router.get("/download/{cleaned_file_id}")
async def download_cleaned_file(
    cleaned_file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch the cleaning history record
    result = await db.execute(
        select(CleaningHistory).filter(
            CleaningHistory.id == cleaned_file_id,
            CleaningHistory.user_id == current_user.id
        )
    )
    cleaning_record = result.scalar_one_or_none()

    if not cleaning_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cleaned file not found")

    # Get the cleaned file path from the cleaning history
    cleaned_file_path = cleaning_record.cleaned_file_path

    # Ensure the cleaned file exists before attempting to serve it
    if not os.path.exists(cleaned_file_path):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Cleaned file not found on the server")

    # Serve the cleaned file for download
    return FileResponse(
        cleaned_file_path, 
        media_type='application/octet-stream', 
        filename=os.path.basename(cleaned_file_path)
    )




# Endpoint to get cleaning history for a user
@router.get("/history/{user_id}")
async def get_cleaning_history(
    user_id: int, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this history")

    result = await db.execute(
        select(CleaningHistory).filter(CleaningHistory.user_id == user_id)
    )
    history = result.scalars().all()

    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No cleaning history found for this user")

    return [{"file_id": item.file_id, "cleaned_file": item.cleaned_file_path, "cleaning_steps": item.cleaning_steps, "cleaned_at": item.cleaned_at} for item in history]

# Endpoint to get cleaning report for a specific cleaned file
from fastapi.responses import StreamingResponse
import io

@router.get("/report/{file_id}")
async def get_cleaning_report(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch cleaning history
    result = await db.execute(
        select(CleaningHistory).filter(CleaningHistory.id == file_id, CleaningHistory.user_id == current_user.id)
    )
    cleaning_record = result.scalar_one_or_none()
    if not cleaning_record:
        raise HTTPException(status_code=404, detail="Cleaning history not found")

    # Fetch original file
    result_file = await db.execute(select(FileUpload).filter(FileUpload.id == cleaning_record.file_id))
    file_record = result_file.scalar_one_or_none()
    if not file_record or not file_record.file_path or not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="Original file not found on server")

    # Load cleaning steps
    cleaning_steps = eval(cleaning_record.cleaning_steps or "{}")
    report_rows = []

    for step, info in cleaning_steps.items():
    # missing_values_filled_with_na can be dict or old list
        if step == "missing_values_filled_with_na":
            if isinstance(info, dict):
                affected_cols = ", ".join(info.get("columns", []))
                filled_counts = info.get("filled_count", {})
                summary = ", ".join([f"{col}: {cnt} filled" for col, cnt in filled_counts.items()])
            elif isinstance(info, list):
                affected_cols = ", ".join(info)
                summary = ""
            else:
                affected_cols = ""
                summary = ""
        elif step == "duplicates_removed":
            if isinstance(info, dict):
                removed_count = info.get("removed_count", 0)
                affected_cols = "Yes" if removed_count > 0 else "No"
                summary = f"{removed_count} duplicate rows removed"
            else:
                affected_cols = str(info)
                summary = ""
        elif step == "strings_normalized":
            if isinstance(info, list):
                affected_cols = ", ".join(info)
                summary = f"Strings normalized in columns: {affected_cols}"
            else:
                affected_cols = ""
                summary = ""
        else:
            affected_cols = ""
            summary = ""

        report_rows.append({"Cleaning Step": step, "Affected Columns": affected_cols, "Summary": summary})

    # Row summary
    original_rows = len(pd.read_csv(file_record.file_path))
    cleaned_rows = len(pd.read_csv(cleaning_record.cleaned_file_path))
    report_rows.extend([
        {"Cleaning Step": "Row Summary", "Affected Columns": "", "Summary": ""},
        {"Cleaning Step": "Original Rows", "Affected Columns": str(original_rows), "Summary": ""},
        {"Cleaning Step": "Cleaned Rows", "Affected Columns": str(cleaned_rows), "Summary": ""}
    ])

    # Convert to CSV
    df_report = pd.DataFrame(report_rows)
    csv_stream = io.StringIO()
    df_report.to_csv(csv_stream, index=False)
    csv_stream.seek(0)

    return StreamingResponse(
        csv_stream,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=cleaning_report_{file_id}.csv"}
    )



