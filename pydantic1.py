from typing import List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ต้องวาง CORS ไว้ตรงนี้ทันที (ใต้ app = FastAPI())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # อนุญาตทั้ง 2 แบบกันเหนียว
    allow_credentials=True,
    allow_methods=["*"], # อนุญาตทุก Method (รวมถึง OPTIONS ด้วย)
    allow_headers=["*"],
)

class Student(BaseModel):
    id: int
    name: str
    score: str 

students = [
    Student(id=1, name="John", score="30"),
    Student(id=2, name="Jack", score="20"),
    Student(id=3, name="Jim", score="40"),
]

@app.get("/students", response_model=List[Student])
async def get_students():
    return students

@app.get("/students/{student_id}", response_model=Student)
async def get_student_by_id(student_id: int):
    for student in students:
        if student.id == student_id:
            return student
            
    raise HTTPException(status_code=404, detail="Student not found")

@app.post("/students", response_model=Student, status_code=status.HTTP_200_OK)
async def create_student(student: Student):
    students.append(student)
    return student

@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
async def delete_student_by_id(student_id: int):
    for index, student in enumerate(students):
        if student.id == student_id:
            delete_student = students.pop(index)
            return {
                "message": "Delete student successfully",
                "data": delete_student
            }
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {student_id} not found"
    )
@app.put("/students/{student_id}", status_code=status.HTTP_200_OK)
async def update_student_by_id(student_id: int, update_student: Student):
    for index, student in enumerate(students):
        if student.id == student_id:
            students[index] = update_student
            return {
                "message": "Update successfully",
                "data": update_student
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Item with ID {student_id} not found"
    )