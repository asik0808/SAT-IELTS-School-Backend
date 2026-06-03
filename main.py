from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os
import json
import base64

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
    email: str

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials_b64 = os.environ.get("GOOGLE_CREDENTIALS")
credentials_json = base64.b64decode(credentials_b64).decode("utf-8")
credentials_info = json.loads(credentials_json)
creds = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
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
            student.email,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        return {"message": "Enrollment successful!"}
    except Exception as e:
        print(f"ERROR: {e}")
        return {"error": str(e)}