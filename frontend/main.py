from fastapi import FastAPI
from database import engine, Base
import models
import auth

# สร้างตารางใน MySQL อัตโนมัติจาก Model
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# นำ Router ของระบบ Auth มารวมในแอปหลัก
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI MySQL Homework Connected Successfully!"}