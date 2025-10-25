# CSV Cleaner API

A simple FastAPI application to clean uploaded CSV files using an AI-powered cleaning agent. Users can upload files, provide custom cleaning instructions (prompts), and get a cleaned version of their data along with a summary of the cleaning steps.

## Features

- User registration and login with JWT authentication
- Upload CSV files
- Clean files automatically using an AI agent (LangChain tool - mock)
- Provide custom cleaning prompts
- Remove duplicates, fill missing values, and normalize string columns
- Store cleaning history for reference
- Download cleaned files (CSV format)
- Download summary reports (CSV format)

## API Endpoints

### Authentication
- `POST /auth/register`: Register a new user with email and password.  
  Returns the created user ID and email.  

- `POST /auth/login`: Log in with email and password.  
  Returns a JWT access token and token type.  

### File Upload
- `POST /files/upload-csv`: Upload a CSV file for cleaning.  
  Returns the uploaded file information.  

### Cleaning
- `POST /clean/{file_id}`: Clean a CSV file by providing the file ID and optional cleaning prompt.  
  Returns the cleaned file, cleaning summary, and AI agent's analysis.  

- `GET /clean/download/{cleaned_file_id}`: Download the cleaned CSV file.  

- `GET /clean/history/{user_id}`: Retrieve the cleaning history for a user.  

- `GET /clean/report/{file_id}`: Get a detailed cleaning report for a specific file.  

## Technologies

- FastAPI
- SQLAlchemy (AsyncSession)
- LangChain agent tool (mock)
- Pandas
- Numpy
- Python 3.10+
- SQLite/PostgreSQL (any supported DB)

## Usage

1. Start the server:
```bash
uvicorn main:app --reload
