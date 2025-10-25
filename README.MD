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

Change the database configuration in `database.py` before starting the server.

```bash
# 1. Activate the virtual environment
venv\Scripts\activate

# 2. Start the server
uvicorn main:app --reload

# 3. Use Swagger Docs to test the API (update the URL according to your local host and port)
http://127.0.0.1:8000/docs

# Note:
# If your FastAPI server runs on a different port, replace 8000 with the actual port number (e.g., http://127.0.0.1:8080/docs)
# You can also access the ReDoc documentation at http://127.0.0.1:8000/redoc

