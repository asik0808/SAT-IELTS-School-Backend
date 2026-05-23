from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openpyxl
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    name: str
    email: str
    phone: str
    course: str

EXCEL_FILE = 'students.xlsx'

def init_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Students"
        ws.append(["Name", "Email", "Phone", "Course"])
        wb.save(EXCEL_FILE)
    
@app.post("/register")
def register(student: Student):
    init_excel()
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active
    ws.append([student.name, student.email, student.phone, student.course])
    wb.save(EXCEL_FILE)
    return {"message": "Student registered successfully"}