from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    phone: str
    course: str
    source: str

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open("SAT-IELTS-School").sheet1

@app.post("/register")
@limiter.limit("3/minute")  # максимум 3 запроса в минуту с одного IP
async def register(request: Request, student: Student):
    try:
        sheet.append_row([
            student.name,
            student.phone,
            student.course,
            student.source,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        return {"message": "Enrollment successful!"}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}