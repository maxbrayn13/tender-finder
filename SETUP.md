# 🛠️ Настройка проекта TenderFinder

Это пошаговое руководство для настройки проекта с нуля.

---

## 📋 Требования

### Обязательно:
- ✅ **Python 3.11+** ([скачать](https://www.python.org/downloads/))
- ✅ **Node.js 18+** ([скачать](https://nodejs.org/))
- ✅ **Git** ([скачать](https://git-scm.com/))

### Опционально:
- **Railway Account** ([регистрация](https://railway.app))
- **GitHub Account** ([регистрация](https://github.com))
- **Docker** (для контейнеризации)

---

## 🚀 Быстрая установка

### Linux / macOS:
```bash
# 1. Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/tender-finder.git
cd tender-finder

# 2. Дайте права на выполнение
chmod +x start.sh

# 3. Запустите
./start.sh
```

### Windows:
```batch
REM 1. Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/tender-finder.git
cd tender-finder

REM 2. Запустите
start.bat
```

---

## 📦 Ручная установка

### Шаг 1: Backend (FastAPI)

```bash
cd backend

# Создать виртуальное окружение
python3 -m venv venv

# Активировать (Linux/Mac)
source venv/bin/activate

# Активировать (Windows)
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env

# Запустить сервер
uvicorn main:app --reload --port 8000
```

**Backend запущен на:** http://localhost:8000  
**API документация:** http://localhost:8000/docs

---

### Шаг 2: Frontend (React + Vite)

Откройте **новый терминал**:

```bash
cd frontend

# Установить зависимости
npm install

# Создать .env файл
cp .env.example .env

# Запустить dev сервер
npm run dev
```

**Frontend запущен на:** http://localhost:3000

---

## 🗄️ База данных

База данных `goszakup_lots.db` уже включена в проект.

### Структура:
- **Таблица**: `lots`
- **Записей**: 99
- **Поля**: id, lot_number, name, price, quantity, category, и др.

### Просмотр данных:
```bash
# Установите SQLite browser
# https://sqlitebrowser.org/

# Откройте файл
backend/goszakup_lots.db
```

---

## 🧪 Тестирование

### Проверка Backend:
```bash
# Health check
curl http://localhost:8000/health

# Получить статистику
curl http://localhost:8000/stats

# Получить лоты
curl http://localhost:8000/lots?limit=5
```

### Проверка Frontend:
Откройте в браузере: http://localhost:3000

Должны увидеть:
- ✅ Главную страницу с поиском
- ✅ 2 калькулятора (по бюджету и марже)
- ✅ Статистику

---

## 🌐 Деплой на Railway

### Метод 1: Через GitHub (рекомендуется)

1. **Загрузите код на GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git
git push -u origin main
```

2. **Подключите к Railway:**
   - Зайдите на [railway.app](https://railway.app)
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

3. **Настройте Backend сервис:**
   - Root Directory: `backend`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     DATABASE_PATH=./goszakup_lots.db
     ```

4. **Настройте Frontend сервис:**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     ```
     VITE_API_URL=https://[backend-url].railway.app
     ```

---

### Метод 2: Через Railway CLI

```bash
# Установка CLI
npm install -g @railway/cli

# Логин
railway login

# Инициализация
railway init

# Deploy Backend
railway up --service backend

# Deploy Frontend
railway up --service frontend
```

---

## 🐳 Docker (опционально)

### Запуск через Docker Compose:
```bash
# Собрать и запустить
docker-compose up --build

# В фоне
docker-compose up -d

# Остановить
docker-compose down
```

---

## 🔧 Настройка переменных окружения

### Backend (.env):
```bash
DATABASE_PATH=./goszakup_lots.db
PORT=8000
```

### Frontend (.env):
```bash
# Для локальной разработки
VITE_API_URL=http://localhost:8000

# Для продакшена
VITE_API_URL=https://your-backend.railway.app
```

---

## 🐛 Решение проблем

### Backend не запускается:
```bash
# Проверьте Python версию
python3 --version  # Должно быть 3.11+

# Переустановите зависимости
pip install --upgrade -r requirements.txt

# Проверьте порт
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Frontend не запускается:
```bash
# Проверьте Node версию
node --version  # Должно быть 18+

# Очистите кэш
rm -rf node_modules package-lock.json
npm install

# Проверьте порт
lsof -i :3000  # Linux/Mac
netstat -ano | findstr :3000  # Windows
```

### CORS ошибка:
Убедитесь что в `backend/main.py` добавлен ваш frontend URL:
```python
allow_origins=[
    "http://localhost:3000",
    "https://your-frontend.railway.app"
]
```

### База данных не найдена:
```bash
# Проверьте путь
ls backend/goszakup_lots.db

# Скопируйте если нужно
cp goszakup_lots.db backend/
```

---

## 📚 Дополнительные ресурсы

- **FastAPI документация**: https://fastapi.tiangolo.com
- **React документация**: https://react.dev
- **Tailwind CSS**: https://tailwindcss.com
- **Railway документация**: https://docs.railway.app
- **Vite документация**: https://vitejs.dev

---

## 🤝 Помощь

Если возникли проблемы:
1. Проверьте логи: `railway logs` (для Railway)
2. Создайте Issue на GitHub
3. Проверьте README.md для дополнительной информации

---

**Готово! 🎉 Теперь вы готовы к разработке!**
