from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    phone: str
    email: str
    course: str

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive"
    
]

creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("SAT-IELTS-School").sheet1

    
@app.post("/register")
def register(student: Student):
    try:
        sheet.append_row([
            student.name,
            student.phone,
            student.email,
            student.course,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        return {"message": "Enrollment successful!"}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}