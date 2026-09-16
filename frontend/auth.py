import datetime
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hash = PasswordHash.recommended()

# สร้างตัวแปรเก็บ Token ที่ถูก Logout แล้ว (Blacklist)
blacklist = set()

@router.post("/register")
async def register(username: str, password: str, db: Session = Depends(get_db)):
    # เช็คว่ามี username นี้ในฐานข้อมูล MySQL หรือยัง
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password ก่อนบันทึก
    hashed_password = password_hash.hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "username": new_user.username}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ค้นหา User จากตารางใน MySQL
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not password_hash.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
   
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)

    token = jwt.encode({
        "sub": user.username,
        "exp": expire
    }, 
    SECRET_KEY, algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # นำ Token เข้า Blacklist เพื่อยกเลิกสิทธิ์
    blacklist.add(token)
    return {"message": "Successfully logged out"}

def get_current_user(token: str = Depends(oauth2_scheme)): 
    # ตรวจสอบว่า Token นี้อยู่ใน Blacklist หรือไม่
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token has been revoked (Logged out)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")