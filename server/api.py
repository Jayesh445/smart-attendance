from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import pandas as pd
from datetime import datetime
import uvicorn
from face_recognition_system import FaceRecognitionSystem

app = FastAPI(title="Face Recognition Attendance API", version="1.0.0")

# Initialize the face recognition system
face_system = FaceRecognitionSystem()

class StudentRegistration(BaseModel):
    student_id: int
    name: str
    email: str

class AttendanceQuery(BaseModel):
    date: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Face Recognition Attendance System API"}

@app.post("/register-student")
async def register_student(student: StudentRegistration):
    """Register a new student"""
    try:
        result = face_system.register_student(student.student_id, student.name, student.email)
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train-model")
async def train_model():
    """Train the face recognition model"""
    try:
        result = face_system.train_model()
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mark-attendance")
async def mark_attendance():
    """Mark attendance using face recognition"""
    try:
        result = face_system.mark_attendance()
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            return JSONResponse(content=result, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attendance-report")
async def get_attendance_report(date: Optional[str] = None):
    """Get attendance report"""
    try:
        records = face_system.get_attendance_report(date)
        return JSONResponse(content={"records": records}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students")
async def get_students():
    """Get list of all registered students"""
    try:
        students = face_system.get_students_list()
        return JSONResponse(content={"students": students}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attendance-stats")
async def get_attendance_stats():
    """Get attendance statistics"""
    try:
        attendance_df = pd.read_csv(face_system.attendance_csv)
        students_df = pd.read_csv(face_system.students_csv)
        
        total_students = len(students_df)
        today_date = datetime.now().strftime('%Y-%m-%d')
        today_attendance = len(attendance_df[attendance_df['date'] == today_date])
        
        stats = {
            "total_students": total_students,
            "today_attendance": today_attendance,
            "attendance_percentage": round((today_attendance / total_students * 100), 2) if total_students > 0 else 0
        }
        
        return JSONResponse(content=stats, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
