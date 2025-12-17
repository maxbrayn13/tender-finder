from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="TenderFinder API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DB_PATH = os.getenv("DATABASE_PATH", "./goszakup_lots.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Models
class Lot(BaseModel):
    id: int
    announce_id: str
    lot_number: str
    original_name: str
    simplified_name: str
    chinese_name: Optional[str]
    category: str
    tender_price: float
    quantity: int
    unit: str
    customer: str
    is_service: int
    suitable_for_china: int
    created_at: str
    status: str

class SearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "margin"
    limit: Optional[int] = 100

class BudgetSearchRequest(BaseModel):
    budget: float
    delivery_percent: Optional[float] = 15.0

class MarginSearchRequest(BaseModel):
    target_margin: float
    delivery_percent: Optional[float] = 15.0

# Helper functions
def calculate_stats(lot: dict, delivery_percent: float = 15.0):
    """Расчет статистики лота"""
    # Для демо используем фиктивные цены источников
    # В реальности нужно парсить источники или хранить в БД
    best_price = lot['tender_price'] * 0.4  # Допустим лучшая цена 40% от тендерной
    
    total_cost = best_price * lot['quantity']
    delivery_cost = round(total_cost * delivery_percent / 100)
    total_expense = total_cost + delivery_cost
    revenue = lot['tender_price'] * lot['quantity']
    profit = revenue - total_expense
    margin_percent = round(((lot['tender_price'] - best_price) / best_price) * 100) if best_price > 0 else 0
    roi = round((profit / total_expense) * 100) if total_expense > 0 else 0
    
    return {
        "best_price": best_price,
        "total_cost": total_cost,
        "delivery_cost": delivery_cost,
        "total_expense": total_expense,
        "revenue": revenue,
        "profit": profit,
        "margin_percent": margin_percent,
        "roi": roi
    }

# Routes
@app.get("/")
async def root():
    return {
        "message": "TenderFinder API v1.0",
        "docs": "/docs",
        "endpoints": {
            "GET /lots": "Получить все лоты",
            "GET /lots/{id}": "Получить лот по ID",
            "POST /lots/search": "Поиск лотов",
            "POST /lots/search-by-budget": "Поиск по бюджету",
            "POST /lots/search-by-margin": "Поиск по марже",
            "GET /stats": "Общая статистика",
            "GET /categories": "Список категорий"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/lots", response_model=List[Lot])
async def get_lots(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Получить список лотов"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM lots WHERE 1=1"
    params = []
    
    if category and category != "all":
        query += " AND category = ?"
        params.append(category)
    
    if search:
        query += " AND (simplified_name LIKE ? OR lot_number LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.get("/lots/{lot_id}")
async def get_lot(lot_id: int):
    """Получить лот по ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots WHERE id = ?", (lot_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Lot not found")
    
    lot = dict(row)
    lot['stats'] = calculate_stats(lot)
    
    return lot

@app.post("/lots/search")
async def search_lots(request: SearchRequest):
    """Расширенный поиск лотов"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM lots WHERE 1=1"
    params = []
    
    if request.query:
        query += " AND (simplified_name LIKE ? OR lot_number LIKE ? OR customer LIKE ?)"
        params.extend([f"%{request.query}%", f"%{request.query}%", f"%{request.query}%"])
    
    if request.category and request.category != "all":
        query += " AND category = ?"
        params.append(request.category)
    
    if request.min_price:
        query += " AND tender_price >= ?"
        params.append(request.min_price)
    
    if request.max_price:
        query += " AND tender_price <= ?"
        params.append(request.max_price)
    
    # Сортировка
    if request.sort_by == "price":
        query += " ORDER BY tender_price ASC"
    elif request.sort_by == "priceDesc":
        query += " ORDER BY tender_price DESC"
    else:
        query += " ORDER BY created_at DESC"
    
    query += f" LIMIT {request.limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        lot = dict(row)
        lot['stats'] = calculate_stats(lot)
        results.append(lot)
    
    # Сортировка по марже/прибыли если нужно
    if request.sort_by == "margin":
        results.sort(key=lambda x: x['stats']['margin_percent'], reverse=True)
    elif request.sort_by == "profit":
        results.sort(key=lambda x: x['stats']['profit'], reverse=True)
    
    return {
        "total": len(results),
        "results": results
    }

@app.post("/lots/search-by-budget")
async def search_by_budget(request: BudgetSearchRequest):
    """Поиск лотов по бюджету (себестоимости)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots")
    rows = cursor.fetchall()
    conn.close()
    
    min_budget = request.budget * 0.8
    max_budget = request.budget * 1.2
    
    results = []
    for row in rows:
        lot = dict(row)
        stats = calculate_stats(lot, request.delivery_percent)
        lot['stats'] = stats
        
        if min_budget <= stats['total_expense'] <= max_budget:
            results.append(lot)
    
    # Сортировка по ROI
    results.sort(key=lambda x: x['stats']['roi'], reverse=True)
    
    return {
        "query": {
            "budget": request.budget,
            "range": [min_budget, max_budget],
            "delivery_percent": request.delivery_percent
        },
        "total": len(results),
        "results": results[:50]  # Ограничение 50 результатов
    }

@app.post("/lots/search-by-margin")
async def search_by_margin(request: MarginSearchRequest):
    """Поиск лотов по желаемой марже (прибыли)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots")
    rows = cursor.fetchall()
    conn.close()
    
    min_margin = request.target_margin * 0.8
    max_margin = request.target_margin * 1.2
    
    results = []
    for row in rows:
        lot = dict(row)
        stats = calculate_stats(lot, request.delivery_percent)
        lot['stats'] = stats
        
        if min_margin <= stats['profit'] <= max_margin:
            results.append(lot)
    
    # Сортировка по ROI
    results.sort(key=lambda x: x['stats']['roi'], reverse=True)
    
    return {
        "query": {
            "target_margin": request.target_margin,
            "range": [min_margin, max_margin],
            "delivery_percent": request.delivery_percent
        },
        "total": len(results),
        "results": results[:50]  # Ограничение 50 результатов
    }

@app.get("/stats")
async def get_stats():
    """Получить общую статистику"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Общее количество
    cursor.execute("SELECT COUNT(*) as total FROM lots")
    total = cursor.fetchone()['total']
    
    # Общая сумма
    cursor.execute("SELECT SUM(tender_price * quantity) as total_sum FROM lots")
    total_sum = cursor.fetchone()['total_sum'] or 0
    
    # Категории
    cursor.execute("SELECT category, COUNT(*) as count FROM lots GROUP BY category")
    categories = [dict(row) for row in cursor.fetchall()]
    
    # Новые сегодня
    cursor.execute("SELECT COUNT(*) as new_today FROM lots WHERE DATE(created_at) = DATE('now')")
    new_today = cursor.fetchone()['new_today']
    
    conn.close()
    
    # Средняя маржа (на основе всех лотов)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots LIMIT 100")
    rows = cursor.fetchall()
    conn.close()
    
    margins = []
    hot_deals = 0
    for row in rows:
        lot = dict(row)
        stats = calculate_stats(lot)
        margins.append(stats['margin_percent'])
        if stats['margin_percent'] >= 100:
            hot_deals += 1
    
    avg_margin = round(sum(margins) / len(margins)) if margins else 0
    
    return {
        "total_lots": total,
        "total_sum": round(total_sum),
        "avg_margin": avg_margin,
        "hot_deals": hot_deals,
        "new_today": new_today,
        "categories": categories
    }

@app.get("/categories")
async def get_categories():
    """Получить список категорий"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM lots WHERE category IS NOT NULL AND category != ''")
    rows = cursor.fetchall()
    conn.close()
    
    return [row['category'] for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
