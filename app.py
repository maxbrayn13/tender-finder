from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import io

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tenderfinder-secret-2025')
CORS(app, supports_credentials=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ИСПОЛЬЗУЕМ ПЕРЕМЕННЫЕ ИЗ RAILWAY
DATABASE_URL = os.getenv('DATABASE_URL')  # Railway автоматически создаёт
USERS_DB_PATH = os.getenv('USERS_DB_PATH', 'users.db')

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
    conn = sqlite3.connect(USERS_DB_PATH)
    cursor = conn.cursor()
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
    admin_exists = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            'INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@tenderfinder.kz', admin_password, 1)
        )
    conn.commit()
    conn.close()

init_users_db()

def pg_query(query, params=None):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or [])
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def pg_query_one(query, params=None):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(query, params or [])
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def calculate_stats(lot):
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

# ═══════════════════════════════════════════════════════════
# НОВЫЙ ЭНДПОИНТ: ПРИЁМ ДАННЫХ ОТ EC2
# ═══════════════════════════════════════════════════════════

@app.route('/api/products/batch', methods=['POST'])
def receive_products():
    """Принять товары от EC2 wrapper"""
    try:
        data = request.get_json()
        lot_number = data.get('lot_number')
        products = data.get('products', [])
        
        if not lot_number or not products:
            return jsonify({"error": "Missing lot_number or products"}), 400
        
        # Логируем получение
        print(f"📥 Получено от EC2: {lot_number}, {len(products)} товаров")
        
        # Сохраняем (если нужно дополнительно кроме PostgreSQL)
        # Или просто подтверждаем приём
        
        return jsonify({
            "status": "success",
            "message": "Products received",
            "lot_number": lot_number,
            "count": len(products)
        }), 200
        
    except Exception as e:
        print(f"❌ Ошибка приёма: {e}")
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Не указаны логин или пароль"}), 400
    
    conn = sqlite3.connect(USERS_DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        user_obj = User(user['id'], user['username'], user['email'], user['is_admin'])
        login_user(user_obj)
        return jsonify({
            "message": "Успешный вход",
            "user": {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "is_admin": bool(user['is_admin'])
            }
        })
    
    return jsonify({"error": "Неверный логин или пароль"}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Вы вышли из системы"})

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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"error": "Не все поля заполнены"}), 400
    
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        
        existing = cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', 
                                 (username, email)).fetchone()
        if existing:
            conn.close()
            return jsonify({"error": "Пользователь уже существует"}), 400
        
        hashed_password = generate_password_hash(password)
        cursor.execute(
            'INSERT INTO users (username, email, password, is_admin) VALUES (?, ?, ?, ?)',
            (username, email, hashed_password, 0)
        )
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            "message": "Регистрация успешна",
            "user": {"id": user_id, "username": username, "email": email, "is_admin": False}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ═══════════════════════════════════════════════════════════
# LOTS API
# ═══════════════════════════════════════════════════════════

@app.route('/api/lots')
@login_required
def get_lots():
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = "SELECT * FROM lots WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        if search:
            query += " AND (simplified_name ILIKE %s OR original_name ILIKE %s OR lot_number ILIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        lots = pg_query(query, params)
        
        count_query = "SELECT COUNT(*) as total FROM lots WHERE 1=1"
        count_params = []
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
        if search:
            count_query += " AND (simplified_name ILIKE %s OR original_name ILIKE %s OR lot_number ILIKE %s)"
            search_term = f"%{search}%"
            count_params.extend([search_term, search_term, search_term])
        if status:
            count_query += " AND status = %s"
            count_params.append(status)
        
        total_result = pg_query_one(count_query, count_params)
        total = total_result['total'] if total_result else 0
        
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
    try:
        lot = pg_query_one("SELECT * FROM lots WHERE id = %s", [lot_id])
        
        if not lot:
            return jsonify({"error": "Лот не найден"}), 404
        
        lot_dict = dict(lot)
        lot_dict['stats'] = calculate_stats(lot_dict)
        
        search_results = pg_query(
            "SELECT * FROM search_results WHERE lot_number = %s ORDER BY created_at DESC",
            [lot['lot_number']]
        )
        lot_dict['search_results'] = [dict(sr) for sr in search_results]
        
        return jsonify(lot_dict)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats')
@login_required
def get_stats():
    try:
        total_lots = pg_query_one("SELECT COUNT(*) as count FROM lots")['count']
        
        status_stats = pg_query(
            "SELECT status, COUNT(*) as count FROM lots GROUP BY status"
        )
        statuses = {row['status']: row['count'] for row in status_stats}
        
        china_suitable = pg_query_one("SELECT COUNT(*) as count FROM lots WHERE suitable_for_china = TRUE")['count']
        services = pg_query_one("SELECT COUNT(*) as count FROM lots WHERE is_service = TRUE")['count']
        searched = pg_query_one("SELECT COUNT(*) as count FROM lots WHERE status = 'searched'")['count']
        total_products = pg_query_one("SELECT COUNT(*) as count FROM search_results")['count']
        
        return jsonify({
            "total_lots": total_lots,
            "statuses": statuses,
            "china_suitable": china_suitable,
            "services": services,
            "searched_lots": searched,
            "total_products": total_products
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories')
@login_required
def get_categories():
    try:
        results = pg_query(
            "SELECT DISTINCT category FROM lots WHERE category IS NOT NULL AND category != '' ORDER BY category"
        )
        categories = [row['category'] for row in results]
        return jsonify({"categories": categories})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search-by-budget', methods=['POST'])
@login_required
def search_by_budget():
    try:
        data = request.get_json()
        budget = float(data.get('budget', 0))
        
        min_budget = budget * 0.8
        max_budget = budget * 1.2
        
        lots = pg_query("SELECT * FROM lots ORDER BY created_at DESC")
        
        suitable_lots = []
        for lot in lots:
            lot_dict = dict(lot)
            stats = calculate_stats(lot_dict)
            if min_budget <= stats['total_expense'] <= max_budget:
                lot_dict['stats'] = stats
                suitable_lots.append(lot_dict)
        
        return jsonify({
            "budget": budget,
            "min": min_budget,
            "max": max_budget,
            "results": suitable_lots
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lots/search-by-margin', methods=['POST'])
@login_required
def search_by_margin():
    try:
        data = request.get_json()
        min_margin = float(data.get('min_margin', 0))
        max_margin = float(data.get('max_margin', 100))
        
        lots = pg_query("SELECT * FROM lots WHERE is_service = FALSE ORDER BY created_at DESC LIMIT 100")
        
        suitable_lots = []
        for lot in lots:
            lot_dict = dict(lot)
            stats = calculate_stats(lot_dict)
            if min_margin <= stats['profit_margin'] <= max_margin:
                lot_dict['stats'] = stats
                suitable_lots.append(lot_dict)
        
        return jsonify({
            "min_margin": min_margin,
            "max_margin": max_margin,
            "results": suitable_lots
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['POST'])
@login_required
def export_lots():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
        
        data = request.get_json()
        lot_ids = data.get('lot_ids', [])
        
        if not lot_ids:
            return jsonify({"error": "Не выбраны лоты"}), 400
        
        placeholders = ','.join(['%s'] * len(lot_ids))
        query = f"SELECT * FROM lots WHERE id IN ({placeholders}) ORDER BY created_at DESC"
        lots = pg_query(query, lot_ids)
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Лоты TenderFinder"
        
        headers = [
            '№', 'Номер лота', 'Оригинальное название', 'Упрощённое название', 
            'Китайское название', 'Цена за единицу', 'Количество', 'Единица',
            'Заказчик', 'Услуга', 'Статус', 'Дата создания'
        ]
        ws.append(headers)
        
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        for idx, lot in enumerate(lots, 1):
            ws.append([
                idx,
                lot.get('lot_number', ''),
                lot.get('original_name', ''),
                lot.get('simplified_name', ''),
                lot.get('chinese_name', ''),
                lot.get('tender_price', 0),
                lot.get('quantity', 0),
                lot.get('unit', ''),
                lot.get('customer', ''),
                'Да' if lot.get('is_service') else 'Нет',
                lot.get('status', ''),
                str(lot.get('created_at', ''))
            ])
        
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'tenderfinder_lots_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users')
@login_required
def get_users():
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        conn.row_factory = sqlite3.Row
        users = conn.execute('SELECT id, username, email, is_admin, created_at FROM users').fetchall()
        conn.close()
        
        return jsonify({"users": [dict(user) for user in users]})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        
        user = cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "Пользователь не найден"}), 404
        
        new_admin_status = 0 if user[0] else 1
        cursor.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_admin_status, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Статус обновлён", "is_admin": bool(new_admin_status)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({"error": "Доступ запрещён"}), 403
    
    if user_id == current_user.id:
        return jsonify({"error": "Нельзя удалить самого себя"}), 400
    
    try:
        conn = sqlite3.connect(USERS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Пользователь удалён"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Главная страница"""
    try:
        return send_file('static/index.html')
    except:
        return app.send_static_file('index.html')

@app.route('/<path:path>')
def catch_all(path):
    """Отлавливаем все остальные запросы"""
    # Если файл существует в static - отдаём его
    try:
        return send_file(f'static/{path}')
    except:
        # Иначе возвращаем index.html (для SPA роутинга)
        try:
            return send_file('static/index.html')
        except:
            return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
