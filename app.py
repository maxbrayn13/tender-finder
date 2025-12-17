from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Database path
DATABASE_PATH = os.getenv('DATABASE_PATH', 'goszakup_lots.db')

def get_db():
    """Подключение к базе данных"""
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

# Frontend route
@app.route('/')
def index():
    """Главная страница"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory('static', path)
    return send_from_directory('static', 'index.html')

# API Routes
@app.route('/api')
def api_root():
    """API информация"""
    return jsonify({
        "message": "TenderFinder API v1.0",
        "endpoints": {
            "health": "/api/health",
            "lots": "/api/lots",
            "stats": "/api/stats",
            "categories": "/api/categories"
        }
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "database": os.path.exists(DATABASE_PATH)
    })

@app.route('/api/lots')
def get_lots():
    """Получить список лотов"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        conn = get_db()
        
        query = "SELECT * FROM lots WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if search:
            query += " AND (simplified_name LIKE ? OR chinese_name LIKE ? OR lot_number LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        lots = conn.execute(query, params).fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as total FROM lots WHERE 1=1"
        count_params = []
        if category:
            count_query += " AND category = ?"
            count_params.append(category)
        if search:
            count_query += " AND (simplified_name LIKE ? OR chinese_name LIKE ? OR lot_number LIKE ?)"
            search_term = f"%{search}%"
            count_params.extend([search_term, search_term, search_term])
        
        total = conn.execute(count_query, count_params).fetchone()['total']
        
        conn.close()
        
        return jsonify({
            "total": total,
            "limit": limit,
            "offset": offset,
            "results": [dict(lot) for lot in lots]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/<int:lot_id>')
def get_lot(lot_id):
    """Получить лот по ID"""
    try:
        conn = get_db()
        lot = conn.execute("SELECT * FROM lots WHERE id = ?", (lot_id,)).fetchone()
        conn.close()
        
        if not lot:
            return jsonify({"error": "Лот не найден"}), 404
        
        lot_dict = dict(lot)
        lot_dict['stats'] = calculate_stats(lot_dict)
        
        return jsonify(lot_dict)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search', methods=['POST'])
def search_lots():
    """Поиск лотов"""
    try:
        data = request.get_json()
        query_text = data.get('query', '')
        category = data.get('category', '')
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        sort_by = data.get('sort_by', 'created_at')
        limit = data.get('limit', 100)
        
        conn = get_db()
        
        query = "SELECT * FROM lots WHERE 1=1"
        params = []
        
        if query_text:
            query += " AND (simplified_name LIKE ? OR chinese_name LIKE ?)"
            search_term = f"%{query_text}%"
            params.extend([search_term, search_term])
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if min_price:
            query += " AND tender_price >= ?"
            params.append(min_price)
        
        if max_price:
            query += " AND tender_price <= ?"
            params.append(max_price)
        
        query += f" ORDER BY {sort_by} DESC LIMIT ?"
        params.append(limit)
        
        lots = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify({
            "total": len(lots),
            "results": [dict(lot) for lot in lots]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search-by-budget', methods=['POST'])
def search_by_budget():
    """Поиск лотов по бюджету"""
    try:
        data = request.get_json()
        budget = float(data.get('budget', 0))
        
        min_budget = budget * 0.8
        max_budget = budget * 1.2
        
        conn = get_db()
        lots = conn.execute("SELECT * FROM lots").fetchall()
        conn.close()
        
        results = []
        for lot in lots:
            lot_dict = dict(lot)
            stats = calculate_stats(lot_dict)
            if min_budget <= stats['total_expense'] <= max_budget:
                lot_dict['stats'] = stats
                results.append(lot_dict)
        
        results.sort(key=lambda x: x['stats']['roi'], reverse=True)
        
        return jsonify({
            "query": {
                "budget": budget,
                "range": [min_budget, max_budget]
            },
            "total": len(results),
            "results": results[:20]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search-by-margin', methods=['POST'])
def search_by_margin():
    """Поиск лотов по марже"""
    try:
        data = request.get_json()
        target_margin = float(data.get('target_margin', 0))
        
        min_margin = target_margin * 0.8
        max_margin = target_margin * 1.2
        
        conn = get_db()
        lots = conn.execute("SELECT * FROM lots").fetchall()
        conn.close()
        
        results = []
        for lot in lots:
            lot_dict = dict(lot)
            stats = calculate_stats(lot_dict)
            if min_margin <= stats['profit'] <= max_margin:
                lot_dict['stats'] = stats
                results.append(lot_dict)
        
        results.sort(key=lambda x: x['stats']['roi'], reverse=True)
        
        return jsonify({
            "query": {
                "target_margin": target_margin,
                "range": [min_margin, max_margin]
            },
            "total": len(results),
            "results": results[:20]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Статистика"""
    try:
        conn = get_db()
        
        total = conn.execute("SELECT COUNT(*) as total FROM lots").fetchone()['total']
        total_sum = conn.execute("SELECT SUM(tender_price * quantity) as total_sum FROM lots").fetchone()['total_sum'] or 0
        
        lots = conn.execute("SELECT * FROM lots").fetchall()
        conn.close()
        
        margins = [calculate_stats(dict(lot))['margin_percent'] for lot in lots]
        avg_margin = sum(margins) / len(margins) if margins else 0
        hot_deals = len([m for m in margins if m > 100])
        
        return jsonify({
            "total_lots": total,
            "total_sum": round(total_sum, 2),
            "avg_margin": round(avg_margin, 2),
            "hot_deals": hot_deals
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories')
def get_categories():
    """Категории"""
    try:
        conn = get_db()
        categories = conn.execute("SELECT DISTINCT category FROM lots WHERE category IS NOT NULL").fetchall()
        conn.close()
        
        return jsonify({
            "categories": [row['category'] for row in categories]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
