from fastapi import FastAPI, Request

app = FastAPI()

students = [
    {
        "id": 1,
        "name": "John Doe",
        "score": 20
    },
    {
        "id": 2,
        "name": "Jim Hanh",
        "score": 40
    },
    {
        "id": 3,
        "name": "Jack Gobert",
        "score": 55
    }
]

@app.get("/students")
def get_all_students():
    return students

@app.get("/students/sum")
def get_students_sum():
    total_score = sum(student["score"] for student in students)
    return {"total_score": total_score}

@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    for student in students:
        if student["id"] == student_id:
            return student
    return {"error": "Student not found"}

@app.post("/check_body")
async def check(request: Request):
    body = await request.json()
    print(body["id"], body["name"])
    return body