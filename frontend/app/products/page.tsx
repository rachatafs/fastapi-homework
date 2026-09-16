"use client";

import { useEffect, useState } from "react";

type Product = {
  id: number;
  name: string;
  description: string;
  price: number;
};

export default function ProductPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [id, setId] = useState("");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  const fetchProducts = async () => {
    try {
      const res = await fetch("http://localhost:8000/products");
      const data = await res.json();
      setProducts(data);
    } catch (error) {
      console.error("Failed to fetch products:", error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isEditing) {
      await fetch(`http://localhost:8000/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: Number(id),
          name: name,
          description: description,
          price: Number(price), 
        }),
      });
      setIsEditing(false); 
    } else {
      await fetch("http://localhost:8000/products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: Number(id),
          name: name,
          description: description,
          price: Number(price), 
        }),
      });
    }
    setId(""); setName(""); setDescription(""); setPrice("");
    fetchProducts(); 
  };

  const handleEdit = (product: Product) => {
    setIsEditing(true); 
    setId(product.id.toString()); 
    setName(product.name);
    setDescription(product.description);
    setPrice(product.price.toString());
  };

  const handleDelete = async (productId: number) => {
    await fetch(`http://localhost:8000/products/${productId}`, {
      method: "DELETE",
    });
    fetchProducts(); 
  };

  return (
    <main className="max-w-2xl mx-auto p-8 font-sans">
      <h1 className="text-3xl font-bold text-blue-600 mb-8 text-center">ระบบจัดการสินค้า (Product CRUD)</h1>
      <form onSubmit={handleSubmit} className="bg-gray-100 p-6 rounded-xl shadow-sm mb-8 space-y-4 text-black">
        <h2 className="text-xl font-bold text-gray-800 mb-4">{isEditing ? "แก้ไขข้อมูลสินค้า" : "เพิ่มสินค้าใหม่"}</h2>
        <div><label className="block text-sm font-medium mb-1">รหัสสินค้า (ID)</label><input type="number" value={id} onChange={(e) => setId(e.target.value)} disabled={isEditing} className={`w-full border border-gray-300 p-2 rounded-lg ${isEditing ? "bg-gray-200" : ""}`} required /></div>
        <div><label className="block text-sm font-medium mb-1">ชื่อสินค้า</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} className="w-full border border-gray-300 p-2 rounded-lg" required /></div>
        <div><label className="block text-sm font-medium mb-1">รายละเอียด (Description)</label><input type="text" value={description} onChange={(e) => setDescription(e.target.value)} className="w-full border border-gray-300 p-2 rounded-lg" required /></div>
        <div><label className="block text-sm font-medium mb-1">ราคา (Price)</label><input type="number" step="any" value={price} onChange={(e) => setPrice(e.target.value)} className="w-full border border-gray-300 p-2 rounded-lg" required /></div>
        <button type="submit" className={`w-full text-white font-bold py-2 rounded-lg transition ${isEditing ? "bg-orange-500" : "bg-blue-600"}`}>{isEditing ? "บันทึกการแก้ไข" : "บันทึกข้อมูล"}</button>
        {isEditing && <button type="button" onClick={() => { setIsEditing(false); setId(""); setName(""); setDescription(""); setPrice(""); }} className="w-full bg-gray-400 text-white font-bold py-2 rounded-lg mt-2">ยกเลิก</button>}
      </form>
      <div>
        <h2 className="text-xl font-bold text-gray-800 mb-4">รายการสินค้าทั้งหมด</h2>
        <div className="space-y-4">
          {products.map((product) => (
            <div key={product.id} className="p-4 border border-gray-300 rounded-lg bg-white text-black flex justify-between items-center">
              <div><p className="font-bold text-lg">ID: {product.id} - {product.name}</p><p className="text-sm">รายละเอียด: {product.description}</p><p className="text-green-600 font-semibold mt-1">ราคา: ฿{product.price}</p></div>
              <div className="space-x-2 flex">
                <button onClick={() => handleEdit(product)} className="bg-yellow-400 text-black px-4 py-2 rounded-lg">Edit</button>
                <button onClick={() => handleDelete(product.id)} className="bg-red-500 text-white px-4 py-2 rounded-lg">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}