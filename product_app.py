from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, create_engine, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
import jwt

# ==========================================
# Step 1: FastAPI App Initialization & CORS
# ==========================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Step 2: MySQL Database Setup
# ==========================================
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/fastapi_homework"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Step 3: Database Table Schema (Many-to-Many)
# ==========================================
product_category_table = Table(
    "product_category",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

class CategoryDB(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    products = relationship("ProductDB", secondary=product_category_table, back_populates="categories")

class ProductDB(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(255))
    price = Column(Float, nullable=False)
    categories = relationship("CategoryDB", secondary=product_category_table, back_populates="products")


# ==========================================
# Step 4: Pydantic Models for Validation
# ==========================================
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    id: int
    name: str
    description: str
    price: float

class ProductCreate(ProductBase):
    categories: List[CategoryCreate] = []

class ProductResponse(ProductBase):
    categories: List[CategoryResponse] = []
    class Config:
        from_attributes = True

Base.metadata.create_all(bind=engine)

# ==========================================
# Step 5: Authentication & JWT Setup
# ==========================================
SECRET_KEY = "mt-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

users = {
    "admin": {
        "username": "admin",
        "password": "1234"
    }
}

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    token = jwt.encode({
        "sub": user["username"]
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==========================================
# Step 6: CRUD API Endpoints (Protected with JWT)
# ==========================================

@app.post("/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_product = ProductDB(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price
    )
    for cat in product.categories:
        db_cat = db.query(CategoryDB).filter(CategoryDB.name == cat.name).first()
        if not db_cat:
            db_cat = CategoryDB(name=cat.name)
        db_product.categories.append(db_cat)
        
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products", response_model=List[ProductResponse])
async def get_products(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product_update: ProductCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    product.name = product_update.name
    product.description = product_update.description
    product.price = product_update.price
    
    product.categories.clear()
    for cat in product_update.categories:
        db_cat = db.query(CategoryDB).filter(CategoryDB.name == cat.name).first()
        if not db_cat:
            db_cat = CategoryDB(name=cat.name)
        product.categories.append(db_cat)
    
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db.delete(product)
    db.commit()
    return {"message": f"Product with id {product_id} has been deleted successfully"}


# ==========================================
# Step 7: Web Interface Endpoint (HTML + Login UI)
# ==========================================
@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    html_content = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>ระบบจัดการสินค้า (Many-to-Many) + Login</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            h1 { text-align: center; color: #333; }
            .card { background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); position: relative; }
            .product-name { font-size: 1.5em; font-weight: bold; color: #007bff; margin-bottom: 5px; }
            .product-price { color: #28a745; font-weight: bold; font-size: 1.2em; }
            .tag { background: #e9ecef; color: #495057; padding: 4px 10px; border-radius: 20px; font-size: 0.85em; margin-right: 5px; display: inline-block; }
            
            /* แผงควบคุมระบบสมาชิก & ปุ่ม */
            .auth-box { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
            .action-panel { display: none; }
            .add-btn { background: #007bff; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .add-btn:hover { background: #0056b3; }
            .edit-btn { position: absolute; top: 20px; right: 20px; background: #ffc107; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .edit-btn:hover { background: #e0a800; }
            .delete-btn { position: absolute; top: 20px; right: 90px; background: #dc3545; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; }
            .delete-btn:hover { background: #c82333; }
            
            /* หน้าต่าง Pop-up (Modal) */
            .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
            .modal-content { background: white; width: 400px; margin: 100px auto; padding: 20px; border-radius: 8px; }
            .modal input, .modal textarea { width: 100%; margin-bottom: 10px; padding: 8px; box-sizing: border-box; }
            .save-btn { background: #28a745; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; border-radius: 5px; font-weight: bold; }
            .save-btn:hover { background: #218838; }
            .close-btn { background: #6c757d; color: white; border: none; padding: 10px; width: 100%; cursor: pointer; border-radius: 5px; margin-top: 10px; font-weight: bold; }
            
            .login-inline input { padding: 6px; margin-right: 5px; }
            .login-inline button { background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📦 ระบบจัดการสินค้า (Many-to-Many)</h1>
            
            <!-- ส่วนล็อกอิน -->
            <div class="auth-box">
                <div id="authStatus">สถานะ: <span style="color: red; font-weight: bold;">ยังไม่ได้เข้าสู่ระบบ</span></div>
                <div id="loginSection" class="login-inline">
                    <input type="text" id="username" placeholder="Username (admin)" value="admin">
                    <input type="password" id="password" placeholder="Password (1234)" value="1234">
                    <button onclick="login()">เข้าสู่ระบบ</button>
                </div>
                <div id="logoutSection" style="display: none;">
                    <span id="welcomeUser" style="margin-right: 10px; font-weight: bold; color: #007bff;"></span>
                    <button onclick="logout()" style="background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">ออกจากระบบ</button>
                </div>
            </div>
            
            <!-- ปุ่มเพิ่มสินค้า (ซ่อนไว้ถ้ายังไม่ Login) -->
            <div id="actionPanel" class="action-panel" style="margin-bottom: 20px; text-align: center;">
                <button class="add-btn" onclick="openAddModal()">➕ เพิ่มสินค้าใหม่</button>
            </div>
            
            <div id="content">
                <p style="text-align: center;">กำลังโหลดข้อมูล...</p>
            </div>
        </div>

        <!-- หน้าต่าง Pop-up สำหรับเพิ่ม/แก้ไขข้อมูล -->
        <div id="productModal" class="modal">
            <div class="modal-content">
                <h3 id="modalTitle" style="margin-top: 0;">สินค้า</h3>
                <input type="hidden" id="modalMode">
                <input type="hidden" id="editId">
                
                <label>ชื่อสินค้า:</label>
                <input type="text" id="editName">
                
                <label>รายละเอียด:</label>
                <textarea id="editDesc" rows="3"></textarea>
                
                <label>ราคา:</label>
                <input type="number" id="editPrice">
                
                <label>หมวดหมู่ (คั่นด้วยลูกน้ำ ,):</label>
                <input type="text" id="editCategories" placeholder="เช่น Electronics, Laptops">
                
                <button class="save-btn" onclick="saveProduct()">บันทึกข้อมูล</button>
                <button class="close-btn" onclick="closeModal()">ยกเลิก</button>
            </div>
        </div>

        <script>
            let currentProducts = [];
            let authToken = localStorage.getItem('jwt_token') || '';

            function checkAuthUI() {
                if (authToken) {
                    document.getElementById('authStatus').innerHTML = 'สถานะ: <span style="color: green; font-weight: bold;">เข้าสู่ระบบแล้ว</span>';
                    document.getElementById('loginSection').style.display = 'none';
                    document.getElementById('logoutSection').style.display = 'block';
                    document.getElementById('actionPanel').style.display = 'block';
                } else {
                    document.getElementById('authStatus').innerHTML = 'สถานะ: <span style="color: red; font-weight: bold;">ยังไม่ได้เข้าสู่ระบบ</span>';
                    document.getElementById('loginSection').style.display = 'block';
                    document.getElementById('logoutSection').style.display = 'none';
                    document.getElementById('actionPanel').style.display = 'none';
                }
            }

            async function login() {
                const u = document.getElementById('username').value;
                const p = document.getElementById('password').value;

                const formData = new URLSearchParams();
                formData.append('username', u);
                formData.append('password', p);

                try {
                    const res = await fetch('/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: formData
                    });

                    if (res.ok) {
                        const data = await res.json();
                        authToken = data.access_token;
                        localStorage.setItem('jwt_token', authToken);
                        checkAuthUI();
                        loadData();
                        alert('เข้าสู่ระบบสำเร็จ!');
                    } else {
                        alert('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง');
                    }
                } catch (err) {
                    alert('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้');
                }
            }

            function logout() {
                authToken = '';
                localStorage.removeItem('jwt_token');
                checkAuthUI();
                loadData();
                alert('ออกจากระบบแล้ว');
            }

            async function loadData() {
                try {
                    const res = await fetch('/products');
                    currentProducts = await res.json();
                    const content = document.getElementById('content');
                    
                    if(currentProducts.length === 0) {
                        content.innerHTML = '<p style="text-align: center;">ยังไม่มีสินค้าในระบบ</p>';
                        return;
                    }

                    const showButtons = authToken !== '';

                    content.innerHTML = currentProducts.map(p => {
                        const tags = p.categories.map(c => `<span class="tag">${c.name}</span>`).join('');
                        const btnHtml = showButtons ? `
                            <button class="delete-btn" onclick="deleteProduct(${p.id})">ลบ</button>
                            <button class="edit-btn" onclick="openEditModal(${p.id})">แก้ไข</button>
                        ` : '';

                        return `
                            <div class="card">
                                ${btnHtml}
                                <div class="product-name">${p.name}</div>
                                <div style="color: #666; margin-bottom: 10px;">${p.description}</div>
                                <div style="margin-bottom: 10px;">
                                    <strong>หมวดหมู่:</strong> ${tags || '<span style="color:#aaa;">ไม่มีหมวดหมู่</span>'}
                                </div>
                                <div class="product-price">฿${p.price.toLocaleString()}</div>
                            </div>
                        `;
                    }).join('');
                } catch (error) {
                    document.getElementById('content').innerHTML = '<p style="color: red; text-align: center;">เกิดข้อผิดพลาดในการเชื่อมต่อ API</p>';
                }
            }

            function openAddModal() {
                document.getElementById('modalTitle').innerText = '➕ เพิ่มสินค้าใหม่';
                document.getElementById('modalMode').value = 'add';
                document.getElementById('editId').value = '';
                document.getElementById('editName').value = '';
                document.getElementById('editDesc').value = '';
                document.getElementById('editPrice').value = '';
                document.getElementById('editCategories').value = '';
                document.getElementById('productModal').style.display = 'block';
            }

            function openEditModal(id) {
                const product = currentProducts.find(p => p.id === id);
                if (!product) return;
                
                document.getElementById('modalTitle').innerText = '✏️ แก้ไขสินค้า';
                document.getElementById('modalMode').value = 'edit';
                document.getElementById('editId').value = product.id;
                document.getElementById('editName').value = product.name;
                document.getElementById('editDesc').value = product.description;
                document.getElementById('editPrice').value = product.price;
                
                const catString = product.categories.map(c => c.name).join(', ');
                document.getElementById('editCategories').value = catString;
                
                document.getElementById('productModal').style.display = 'block';
            }

            function closeModal() {
                document.getElementById('productModal').style.display = 'none';
            }

            async function saveProduct() {
                const mode = document.getElementById('modalMode').value;
                const name = document.getElementById('editName').value;
                const desc = document.getElementById('editDesc').value;
                const price = parseFloat(document.getElementById('editPrice').value);
                const catString = document.getElementById('editCategories').value;
                
                if(!name || isNaN(price)) {
                    alert('กรุณากรอกชื่อสินค้าและราคาให้ถูกต้อง');
                    return;
                }

                let id = document.getElementById('editId').value;
                if(mode === 'add') {
                    const maxId = currentProducts.length > 0 ? Math.max(...currentProducts.map(p => p.id)) : 0;
                    id = maxId + 1;
                } else {
                    id = parseInt(id);
                }
                
                const categoriesArray = catString.split(',').map(s => s.trim()).filter(s => s !== '').map(name => ({ name: name }));
                
                const payload = {
                    id: id,
                    name: name,
                    description: desc || "",
                    price: price,
                    categories: categoriesArray
                };

                const method = mode === 'add' ? 'POST' : 'PUT';
                const url = mode === 'add' ? '/products' : `/products/${id}`;

                try {
                    const response = await fetch(url, {
                        method: method,
                        headers: { 
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${authToken}`
                        },
                        body: JSON.stringify(payload)
                    });

                    if (response.ok) {
                        closeModal();
                        loadData(); 
                    } else {
                        alert('เกิดข้อผิดพลาดในการบันทึกข้อมูล (กรุณาเข้าสู่ระบบก่อน)');
                    }
                } catch (error) {
                    alert('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้');
                }
            }

            async function deleteProduct(id) {
                if(!confirm('คุณแน่ใจหรือไม่ว่าต้องการลบสินค้านี้?')) return;
                
                try {
                    const response = await fetch(`/products/${id}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${authToken}`
                        }
                    });

                    if (response.ok) {
                        loadData(); 
                    } else {
                        alert('ลบข้อมูลไม่สำเร็จ (กรุณาเข้าสู่ระบบก่อน)');
                    }
                } catch (error) {
                    alert('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้');
                }
            }

            checkAuthUI();
            loadData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)