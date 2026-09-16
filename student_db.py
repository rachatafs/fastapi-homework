from typing import List
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Step:1 SQLite
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# สร้างโครงสร้างตาราง (Table Schema)
class StudentDB(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    score = Column(Float, nullable=False)

class Student(BaseModel):
    id: int
    name: str
    score: float

#in
class StudentCreate(Student):
    pass

#out
class StudentResponse(Student):
    id: int
    class Config:
        from_attributes = True

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

# 1. เพิ่มข้อมูลนักศึกษา (ทีละ 1 คน)
@app.post("/students", response_model=StudentResponse)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = StudentDB(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

# 2. เพิ่มข้อมูลนักศึกษา (ทีละหลายคนพร้อมกัน)
@app.post("/students/multiple", response_model=List[StudentResponse])
async def create_multiple_students(students: List[StudentCreate], db: Session = Depends(get_db)):
    db_students = [StudentDB(**student.model_dump()) for student in students]
    db.add_all(db_students)
    db.commit()
    for db_student in db_students:
        db.refresh(db_student)
    return db_students

# 3. ดึงข้อมูลนักศึกษาทั้งหมด
@app.get("/students", response_model=List[StudentResponse])
async def get_students(db: Session = Depends(get_db)):
    students = db.query(StudentDB).all()
    return students

# 4. ดึงข้อมูลนักศึกษาทีละคนตาม ID
@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    return student

# 5. ลบข้อมูลนักศึกษาตาม ID
@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    # ค้นหาคนที่จะลบ
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    
    # ถ้าไม่เจอให้แจ้ง Error 404
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # สั่งลบข้อมูลออกจากฐานข้อมูล
    db.delete(student)
    db.commit()
    
    return {"message": f"Student with id {student_id} has been deleted successfully"}

# 6. อัปเดตข้อมูลนักศึกษาตาม ID (PUT)
@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(student_id: int, student_update: StudentCreate, db: Session = Depends(get_db)):
    # ค้นหาว่ามีนักศึกษาคนนี้อยู่ในระบบไหม
    student = db.query(StudentDB).filter(StudentDB.id == student_id).first()
    
    # ถ้าไม่เจอให้แจ้ง Error 404
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # อัปเดตข้อมูลใหม่ทับข้อมูลเดิม
    student.name = student_update.name
    student.score = student_update.score
    
    db.commit()
    db.refresh(student)
    
    return student 