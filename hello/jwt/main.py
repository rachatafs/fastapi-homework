from fastapi import FastAPI
from students import router as students_router
from auth import router as auth_router  # ต้อง import ไฟล์ auth เข้ามาด้วยครับ

app = FastAPI()

app.include_router(auth_router)
app.include_router(students_router, prefix="/students") # แนะนำให้ใส่ prefix เพื่อแยก URL ของนักศึกษาออกมาครับ