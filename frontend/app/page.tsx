"use client";

import { useEffect, useState } from "react";

// กำหนดโครงสร้างข้อมูลให้ตรงกับ Backend
type Student = {
  id: number;
  name: string;
  score: string;
};

export default function Home() {
  const [students, setStudents] = useState<Student[]>([]);
  
  // State สำหรับเก็บค่าในช่องกรอกข้อมูล
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [score, setScore] = useState("");

  // State ใหม่: เช็คว่ากำลัง "แก้ไขโหมด" อยู่หรือไม่
  const [isEditing, setIsEditing] = useState(false);

  // 1. ฟังก์ชันดึงข้อมูล (GET)
  const fetchStudents = async () => {
    const res = await fetch("http://localhost:8000/students");
    const data = await res.json();
    setStudents(data);
  };

  // ดึงข้อมูลทันทีที่เปิดหน้าเว็บ
  useEffect(() => {
    fetchStudents();
  }, []);

  // 2. ฟังก์ชัน Submit สำหรับทำหน้าที่ทั้ง Add (POST) และ Edit (PUT)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isEditing) {
      // โหมดแก้ไข: ยิง PUT ไปที่ API
      await fetch(`http://localhost:8000/students/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: Number(id),
          name: name,
          score: String(score), 
        }),
      });
      setIsEditing(false); // แก้ไขเสร็จ ปิดโหมดแก้ไข
    } else {
      // โหมดเพิ่มข้อมูลใหม่: ยิง POST ไปที่ API
      await fetch("http://localhost:8000/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: Number(id),
          name: name,
          score: String(score), 
        }),
      });
    }

    // ล้างค่าในฟอร์ม และดึงข้อมูลใหม่มาแสดง
    setId("");
    setName("");
    setScore("");
    fetchStudents(); 
  };

  // 3. ฟังก์ชันเตรียมแก้ไขข้อมูล (เมื่อกดปุ่ม Edit สีเหลือง)
  const handleEdit = (student: Student) => {
    setIsEditing(true); 
    setId(student.id.toString()); // ดึงข้อมูลเก่ามาใส่ในช่องกรอก
    setName(student.name);
    setScore(student.score);
  };

  // 4. ฟังก์ชันลบข้อมูล (DELETE)
  const handleDelete = async (studentId: number) => {
    await fetch(`http://localhost:8000/students/${studentId}`, {
      method: "DELETE",
    });
    fetchStudents(); 
  };

  return (
    <main className="max-w-2xl mx-auto p-8 font-sans">
      <h1 className="text-3xl font-bold text-blue-600 mb-8 text-center">
        ระบบจัดการนักศึกษา (Full-Stack CRUD)
      </h1>

      {/* ฟอร์มกรอกข้อมูล */}
      <form onSubmit={handleSubmit} className="bg-gray-100 p-6 rounded-xl shadow-sm mb-8 space-y-4 text-black">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          {isEditing ? "แก้ไขข้อมูลนักศึกษา" : "เพิ่มข้อมูลใหม่"}
        </h2>
        
        <div>
          <label className="block text-sm font-medium mb-1">รหัสนักศึกษา (ID)</label>
          <input 
            type="number" 
            value={id}
            onChange={(e) => setId(e.target.value)}
            disabled={isEditing} // ล็อก ID ไว้ตอนแก้ ป้องกันการเผลอเปลี่ยนรหัส
            className={`w-full border border-gray-300 p-2 rounded-lg ${isEditing ? "bg-gray-200" : ""}`}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">ชื่อ-นามสกุล</label>
          <input 
            type="text" 
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-gray-300 p-2 rounded-lg"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">คะแนน</label>
          <input 
            type="number" 
            value={score}
            onChange={(e) => setScore(e.target.value)}
            className="w-full border border-gray-300 p-2 rounded-lg"
            required
          />
        </div>

        {/* ปุ่ม Submit ที่เปลี่ยนสีและข้อความตามโหมด */}
        <button 
          type="submit" 
          className={`w-full text-white font-bold py-2 rounded-lg transition ${
            isEditing ? "bg-orange-500 hover:bg-orange-600" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {isEditing ? "บันทึกการแก้ไข" : "บันทึกข้อมูล"}
        </button>

        {/* ปุ่มยกเลิก (จะโผล่มาเฉพาะตอนอยู่ในโหมด Edit) */}
        {isEditing && (
          <button 
            type="button"
            onClick={() => {
              setIsEditing(false);
              setId(""); setName(""); setScore("");
            }}
            className="w-full bg-gray-400 text-white font-bold py-2 rounded-lg hover:bg-gray-500 transition mt-2"
          >
            ยกเลิก
          </button>
        )}
      </form>

      {/* แสดงรายชื่อ */}
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4 text-white">รายชื่อนักศึกษาทั้งหมด</h2>
        <div className="space-y-4">
          {students.map((student) => (
            <div 
              key={student.id} 
              className="p-4 border border-gray-300 rounded-lg shadow-sm bg-white text-black flex justify-between items-center"
            >
              <div>
                <p className="font-bold text-lg text-gray-800">ID: {student.id}</p>
                <p className="text-gray-700">ชื่อ: {student.name}</p>
                <p className="text-green-600 font-semibold mt-1">คะแนน: {student.score}</p>
              </div>
              
              <div className="space-x-2">
                {/* ปุ่ม Edit */}
                <button 
                  onClick={() => handleEdit(student)}
                  className="bg-yellow-400 text-black px-4 py-2 rounded-lg hover:bg-yellow-500 transition"
                >
                  Edit
                </button>
                {/* ปุ่ม Delete */}
                <button 
                  onClick={() => handleDelete(student.id)}
                  className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
          
          {students.length === 0 && (
            <p className="text-center text-gray-500 mt-4">ไม่มีข้อมูลนักศึกษาในระบบ</p>
          )}
        </div>
      </div>
    </main>
  );
}