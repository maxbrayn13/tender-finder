from flask import Flask, jsonify, request, send_from_directory, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database paths
DATABASE_PATH = os.getenv('DATABASE_PATH', 'goszakup_lots.db')
USERS_DB_PATH = os.getenv('USERS_DB_PATH', 'users.db')

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
    
    # Создать админа по умолчанию
    admin_exists = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@tenderfinder.kz', admin_password, 1))
    
    conn.commit()
    conn.close()

# Инициализация при запуске
init_users_db()

def get_db():
    """Подключение к базе данных лотов"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_users_db():
    """Подключение к базе данных пользователей"""
    conn = sqlite3.connect(USERS_DB_PATH)
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

# ============= FRONTEND ROUTES =============

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

# ============= AUTH API ROUTES =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            return jsonify({"error": "Все поля обязательны"}), 400
        
        conn = get_users_db()
        
        # Проверка существования
        existing = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                              (username, email)).fetchone()
        if existing:
            conn.close()
            return jsonify({"error": "Пользователь уже существует"}), 400
        
        # Создание пользователя
        hashed_password = generate_password_hash(password)
        cursor = conn.execute('''
            INSERT INTO users (username, email, password, is_admin)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, 0))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Автоматический вход
        user = User(user_id, username, email, False)
        login_user(user)
        
        return jsonify({
            "message": "Регистрация успешна",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "is_admin": False
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Вход пользователя"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Введите логин и пароль"}), 400
        
        conn = get_users_db()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', 
                                (username,)).fetchone()
        conn.close()
        
        if not user_data or not check_password_hash(user_data['password'], password):
            return jsonify({"error": "Неверный логин или пароль"}), 401
        
        user = User(user_data['id'], user_data['username'], 
                   user_data['email'], user_data['is_admin'])
        login_user(user)
        
        return jsonify({
            "message": "Вход выполнен",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            }
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Выход пользователя"""
    logout_user()
    return jsonify({"message": "Выход выполнен"})

@app.route('/api/auth/me')
@login_required
def get_current_user():
    """Получить текущего пользователя"""
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin
    })

# ============= ADMIN API ROUTES =============

@app.route('/api/admin/users')
@login_required
def admin_get_users():
    """Получить всех пользователей (только для админа)"""
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    try:
        conn = get_users_db()
        users = conn.execute('SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC').fetchall()
        conn.close()
        
        return jsonify({
            "users": [dict(user) for user in users]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    """Переключить статус админа (только для админа)"""
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    if user_id == current_user.id:
        return jsonify({"error": "Нельзя изменить свои права"}), 400
    
    try:
        conn = get_users_db()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not user:
            conn.close()
            return jsonify({"error": "Пользователь не найден"}), 404
        
        new_status = 0 if user['is_admin'] else 1
        conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({
            "message": "Статус обновлён",
            "is_admin": bool(new_status)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def admin_delete_user(user_id):
    """Удалить пользователя (только для админа)"""
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    if user_id == current_user.id:
        return jsonify({"error": "Нельзя удалить себя"}), 400
    
    try:
        conn = get_users_db()
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Пользователь удалён"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= PUBLIC API ROUTES =============

@app.route('/api')
def api_root():
    """API информация"""
    return jsonify({
        "message": "TenderFinder API v2.0 with Auth",
        "authenticated": current_user.is_authenticated,
        "endpoints": {
            "auth": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "logout": "/api/auth/logout",
                "me": "/api/auth/me"
            },
            "public": {
                "health": "/api/health",
                "stats": "/api/stats"
            },
            "protected": {
                "lots": "/api/lots",
                "search": "/api/lots/search-by-budget"
            },
            "admin": {
                "users": "/api/admin/users"
            }
        }
    })

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "database": os.path.exists(DATABASE_PATH),
        "users_db": os.path.exists(USERS_DB_PATH)
    })

# ============= PROTECTED API ROUTES =============

@app.route('/api/lots')
@login_required
def get_lots():
    """Получить список лотов (требует авторизации)"""
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
@login_required
def get_lot(lot_id):
    """Получить лот по ID (требует авторизации)"""
    try:
        conn = get_db()
        lot = conn.execute("SELECT * FROM lots WHERE id = ?", (lot_id,)).fetchone()
        
        if not lot:
            conn.close()
            return jsonify({"error": "Лот не найден"}), 404
        
        lot_dict = dict(lot)
        lot_dict['stats'] = calculate_stats(lot_dict)
        
        # Получить результаты поиска (ссылки на магазины)
        search_results = conn.execute(
            "SELECT * FROM search_results WHERE lot_id = ? ORDER BY product_price",
            (lot_id,)
        ).fetchall()
        lot_dict['search_results'] = [dict(sr) for sr in search_results]
        
        conn.close()
        
        return jsonify(lot_dict)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search-by-budget', methods=['POST'])
@login_required
def search_by_budget():
    """Поиск лотов по бюджету (требует авторизации)"""
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
@login_required
def search_by_margin():
    """Поиск лотов по марже (требует авторизации)"""
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
    """Статистика (публичный доступ)"""
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
    """Категории (публичный доступ)"""
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
