from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import os
from pathlib import Path

app = FastAPI(
    title="TenderFinder API",
    description="API для поиска выгодных госзакупок Казахстана",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "./goszakup_lots.db")

# Static files для frontend
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_stats(lot):
    """Расчёт статистики для лота"""
    best_price = lot['tender_price'] * 0.4
    total_cost = best_price * lot['quantity']
    delivery_cost = total_cost * 0.15
    total_expense = total_cost + delivery_cost
    revenue = lot['tender_price'] * lot['quantity']
    profit = revenue - total_expense
    margin_percent = ((lot['tender_price'] - best_price) / best_price) * 100
    roi = (profit / total_expense) * 100 if total_expense > 0 else 0
    
    return {
        "best_price": round(best_price, 2),
        "total_cost": round(total_cost, 2),
        "delivery_cost": round(delivery_cost, 2),
        "total_expense": round(total_expense, 2),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "margin_percent": round(margin_percent, 2),
        "roi": round(roi, 2)
    }

# Models
class Lot(BaseModel):
    id: int
    announce_id: Optional[str]
    lot_number: Optional[str]
    original_name: Optional[str]
    simplified_name: Optional[str]
    chinese_name: Optional[str]
    category: Optional[str]
    tender_price: float
    quantity: int
    unit: Optional[str]
    customer: Optional[str]
    is_service: Optional[int]
    suitable_for_china: Optional[int]
    created_at: Optional[str]
    status: Optional[str]

class SearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[str] = "created_at"
    limit: int = 100

class BudgetSearchRequest(BaseModel):
    budget: float
    delivery_percent: float = 15.0

class MarginSearchRequest(BaseModel):
    target_margin: float
    delivery_percent: float = 15.0

# API Routes
@app.get("/api")
def api_root():
    return {
        "message": "TenderFinder API v1.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "lots": "/api/lots",
            "stats": "/api/stats",
            "categories": "/api/categories"
        }
    }

@app.get("/api/health")
def health():
    return {"status": "healthy", "database": os.path.exists(DATABASE_PATH)}

@app.get("/api/lots")
def get_lots(limit: int = 100, offset: int = 0, category: Optional[str] = None, search: Optional[str] = None):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM lots WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if search:
        query += " AND (simplified_name LIKE ? OR chinese_name LIKE ? OR lot_number LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term])
    
    query += f" ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    lots = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT COUNT(*) as total FROM lots")
    total = cursor.fetchone()['total']
    
    conn.close()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": lots
    }

@app.get("/api/lots/{lot_id}")
def get_lot(lot_id: int):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM lots WHERE id = ?", (lot_id,))
    lot = cursor.fetchone()
    
    if not lot:
        raise HTTPException(status_code=404, detail="Лот не найден")
    
    lot_dict = dict(lot)
    lot_dict['stats'] = calculate_stats(lot_dict)
    
    conn.close()
    return lot_dict

@app.post("/api/lots/search")
def search_lots(request: SearchRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM lots WHERE 1=1"
    params = []
    
    if request.query:
        query += " AND (simplified_name LIKE ? OR chinese_name LIKE ?)"
        search_term = f"%{request.query}%"
        params.extend([search_term, search_term])
    
    if request.category:
        query += " AND category = ?"
        params.append(request.category)
    
    if request.min_price:
        query += " AND tender_price >= ?"
        params.append(request.min_price)
    
    if request.max_price:
        query += " AND tender_price <= ?"
        params.append(request.max_price)
    
    query += f" ORDER BY {request.sort_by} DESC LIMIT ?"
    params.append(request.limit)
    
    cursor.execute(query, params)
    lots = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "total": len(lots),
        "results": lots
    }

@app.post("/api/lots/search-by-budget")
def search_by_budget(request: BudgetSearchRequest):
    """Поиск лотов по бюджету (±20%)"""
    min_budget = request.budget * 0.8
    max_budget = request.budget * 1.2
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots")
    lots = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    results = []
    for lot in lots:
        stats = calculate_stats(lot)
        if min_budget <= stats['total_expense'] <= max_budget:
            lot['stats'] = stats
            results.append(lot)
    
    results.sort(key=lambda x: x['stats']['roi'], reverse=True)
    
    return {
        "query": {
            "budget": request.budget,
            "range": [min_budget, max_budget]
        },
        "total": len(results),
        "results": results[:20]
    }

@app.post("/api/lots/search-by-margin")
def search_by_margin(request: MarginSearchRequest):
    """Поиск лотов по марже (±20%)"""
    min_margin = request.target_margin * 0.8
    max_margin = request.target_margin * 1.2
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lots")
    lots = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    results = []
    for lot in lots:
        stats = calculate_stats(lot)
        if min_margin <= stats['profit'] <= max_margin:
            lot['stats'] = stats
            results.append(lot)
    
    results.sort(key=lambda x: x['stats']['roi'], reverse=True)
    
    return {
        "query": {
            "target_margin": request.target_margin,
            "range": [min_margin, max_margin]
        },
        "total": len(results),
        "results": results[:20]
    }

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM lots")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT SUM(tender_price * quantity) as total_sum FROM lots")
    total_sum = cursor.fetchone()['total_sum'] or 0
    
    cursor.execute("SELECT * FROM lots")
    lots = [dict(row) for row in cursor.fetchall()]
    
    margins = [calculate_stats(lot)['margin_percent'] for lot in lots]
    avg_margin = sum(margins) / len(margins) if margins else 0
    
    hot_deals = len([m for m in margins if m > 100])
    
    conn.close()
    
    return {
        "total_lots": total,
        "total_sum": round(total_sum, 2),
        "avg_margin": round(avg_margin, 2),
        "hot_deals": hot_deals
    }

@app.get("/api/categories")
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT category FROM lots WHERE category IS NOT NULL")
    categories = [row['category'] for row in cursor.fetchall()]
    
    conn.close()
    return {"categories": categories}

# Frontend route - serve React app
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve React frontend"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not built. Build React app and place in /static"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
