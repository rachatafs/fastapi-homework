import datetime
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

router = APIRouter()

SECRET_KEY = "my-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

password_hash = PasswordHash.recommended()
hashed = password_hash.hash("1234")

users = {
    "admin":
    { 
        "username": "admin",
        "password": hashed
    }
}

# สร้างตัวแปรเก็บ Token ที่ถูก Logout แล้ว (Blacklist)
blacklist = set()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data.username)
    print(form_data.password)
    user = users.get(form_data.username)

    print(user["password"])

    if not user or not password_hash.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
   
    print(user)

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1)

    token = jwt.encode({
        "sub": user["username"],
        "exp": expire
    }, 
    SECRET_KEY, algorithm=ALGORITHM
    )

    return {
        "access_token" : token,
        "token_type": "bearer"
    }

@router.get("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    # นำ Token ที่ใช้งานอยู่ใส่เข้า Blacklist เพื่อยกเลิกสิทธิ์
    blacklist.add(token)
    return {"message": "Successfully logged out"}

def get_current_user(token: str = Depends(oauth2_scheme)): 
    # ตรวจสอบว่า Token นี้อยู่ใน Blacklist หรือไม่ (ถ้าอยู่แปลว่า Logout ไปแล้ว ห้ามเข้า)
    if token in blacklist:
        raise HTTPException(status_code=401, detail="Token has been revoked (Logged out)")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        print(f"username: =  {username}")

        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")