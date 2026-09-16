from fastapi import APIRouter, Depends
from auth import get_current_user

router = APIRouter()

@router.get("/")
async def hello1():
    return { "mesg": "xxx"}

# Must request with access Bearer token
@router.get("/students")
async def get_students( username: str = Depends(get_current_user)  ):
    print("Get students")
    return {
        "message": "Authenticated user",
        "user" : username,
        "students" :[
            {"id" : 1, "name": "John"},
            {"id" : 2, "name": "Jack"}
        ]
    }