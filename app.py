from flask import Flask, jsonify, request, send_from_directory, send_file, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tenderfinder-secret-2025')
CORS(app, supports_credentials=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ВАЖНО: PostgreSQL для лотов, SQLite для пользователей
DATABASE_URL = os.getenv('DATABASE_URL')  # Railway PostgreSQL для лотов
USERS_DB_PATH = os.getenv('USERS_DB_PATH', 'users.db')  # SQLite для пользователей

# User model
class User(UserMixin):
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'], user['is_admin'])
    return None

def init_users_db():
    """Инициализация базы данных пользователей"""
    conn = sqlite3.connect(USERS_DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создать админа если нет
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        hashed_password = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@tenderfinder.com', hashed_password, 1)
        )
    
    conn.commit()
    conn.close()

init_users_db()

def get_users_db():
    """Подключение к базе данных пользователей"""
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# PostgreSQL helper functions
def pg_query(query, params=None):
    """Выполнить SELECT запрос к PostgreSQL"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or [])
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def pg_query_one(query, params=None):
    """Выполнить SELECT запрос и получить одну строку"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or [])
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def calculate_stats(lot):
    """Расчёт статистики для лота"""
    best_price = lot['tender_price'] * 0.4
    total_cost = best_price * lot['quantity']
    delivery_cost = total_cost * 0.15
    total_expense = total_cost + delivery_cost
    revenue = lot['tender_price'] * lot['quantity']
    profit = revenue - total_expense
    profit_margin = (profit / revenue * 100) if revenue > 0 else 0
    
    return {
        'best_price': round(best_price, 2),
        'total_cost': round(total_cost, 2),
        'delivery_cost': round(delivery_cost, 2),
        'total_expense': round(total_expense, 2),
        'revenue': round(revenue, 2),
        'profit': round(profit, 2),
        'profit_margin': round(profit_margin, 2)
    }

# ============= EC2 DATA RECEIVING ENDPOINT =============

@app.route('/api/products/batch', methods=['POST'])
def receive_products_batch():
    """Принять товары от EC2 wrapper"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        lot_number = data.get('lot_number')
        products = data.get('products', [])
        lot_info = data.get('lot_info', {})
        
        if not lot_number:
            return jsonify({"error": "Missing lot_number"}), 400
        
        # Логируем получение
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] 📥 Получено от EC2:")
        print(f"   Лот: {lot_number}")
        print(f"   Товаров: {len(products)}")
        
        return jsonify({
            "status": "success",
            "message": "Products received successfully",
            "lot_number": lot_number,
            "products_count": len(products),
            "timestamp": timestamp
        }), 200
        
    except Exception as e:
        print(f"❌ Ошибка приёма: {e}")
        return jsonify({"status": "error", "error": str(e)}), 500

# ============= AUTHENTICATION =============

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Не указаны логин или пароль"}), 400
    
    conn = get_users_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password'], password):
        return jsonify({"error": "Неверный логин или пароль"}), 401
    
    user_obj = User(user['id'], user['username'], user['email'], user['is_admin'])
    login_user(user_obj)
    
    return jsonify({
        "message": "Вход выполнен",
        "user": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "is_admin": bool(user['is_admin'])
        }
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Выход выполнен"})

@app.route('/api/check-auth')
def check_auth():
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "is_admin": current_user.is_admin
            }
        })
    return jsonify({"authenticated": False})

# ============= LOTS API (PostgreSQL) =============

@app.route('/api/lots')
@login_required
def get_lots():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        
        query = "SELECT * FROM lots WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if search:
            query += " AND (simplified_name ILIKE %s OR original_name ILIKE %s OR lot_number ILIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        lots = pg_query(query, params)
        
        # Добавляем статистику
        lots_with_stats = []
        for lot in lots:
            lot_dict = dict(lot)
            lot_dict['stats'] = calculate_stats(lot)
            lots_with_stats.append(lot_dict)
        
        return jsonify({
            "lots": lots_with_stats,
            "total": len(lots)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/<lot_number>')
@login_required
def get_lot_detail(lot_number):
    try:
        # Получаем лот
        lot = pg_query_one("SELECT * FROM lots WHERE lot_number = %s", [lot_number])
        
        if not lot:
            return jsonify({"error": "Лот не найден"}), 404
        
        # Получаем товары
        products = pg_query(
            "SELECT * FROM search_results WHERE lot_number = %s",
            [lot_number]
        )
        
        lot_dict = dict(lot)
        lot_dict['stats'] = calculate_stats(lot)
        lot_dict['products'] = [dict(p) for p in products]
        
        return jsonify(lot_dict)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories')
@login_required
def get_categories():
    try:
        categories = pg_query("SELECT DISTINCT category FROM lots WHERE category IS NOT NULL")
        return jsonify({
            "categories": [c['category'] for c in categories if c['category']]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
@login_required
def get_stats():
    try:
        total_lots = pg_query_one("SELECT COUNT(*) as count FROM lots")
        total_products = pg_query_one("SELECT COUNT(*) as count FROM search_results")
        
        return jsonify({
            "total_lots": total_lots['count'] if total_lots else 0,
            "total_products": total_products['count'] if total_products else 0
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= STATIC FILES =============

@app.route('/')
def index():
    """Главная страница"""
    try:
        return send_file('static/index.html')
    except:
        return app.send_static_file('index.html')

@app.route('/<path:path>')
def catch_all(path):
    """Отловить все запросы"""
    try:
        return send_file(f'static/{path}')
    except:
        try:
            return send_file('static/index.html')
        except:
            return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
