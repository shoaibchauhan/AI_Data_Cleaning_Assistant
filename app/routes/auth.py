import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import UserCreate, UserOut, Token
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_access_token
from app.database import get_db
from fastapi import Form
from fastapi import HTTPException, status
import logging
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/auth", tags=["auth"])

logging.basicConfig(level=logging.DEBUG)

class EmailAlreadyRegisteredException(HTTPException):
    def __init__(self, detail: str = "Email already registered"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Check if user exists
        result = await db.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        # If user already exists, raise a specific exception
        if existing_user:
            raise EmailAlreadyRegisteredException()

        # Create new user if not exists
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except EmailAlreadyRegisteredException as e:
        # Handle the already-registered error explicitly
        logging.warning(f"User registration failed: {e.detail}")
        raise e  # Re-raise the exception to return the HTTP response
    except SQLAlchemyError as e:
        # Handle database-specific errors
        logging.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        # Catch-all for other exceptions
        logging.error(f"Unexpected error during registration: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

from sqlalchemy.exc import SQLAlchemyError

@router.post("/login", response_model=Token)
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
    
    except SQLAlchemyError as e:
        logging.error(f"Database error during login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error")
    except Exception as e:
        logging.error(f"Error during login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
