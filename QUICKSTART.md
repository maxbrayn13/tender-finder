# ⚡ QUICKSTART - TenderFinder

## 🎯 Цель
Запустить TenderFinder локально ЗА 5 МИНУТ и задеплоить на Railway ЗА 10 МИНУТ.

---

## 📦 ШАГ 1: Локальный запуск (5 минут)

### Скачайте и распакуйте проект
```bash
# После скачивания tender-finder-complete.zip
unzip tender-finder-complete.zip
cd tender-finder-app
```

### Запустите одной командой

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```batch
start.bat
```

### Откройте в браузере
- http://localhost:3000 - Frontend
- http://localhost:8000/docs - API документация

**✅ Готово! Приложение работает локально!**

---

## 🌐 ШАГ 2: Деплой на Railway (10 минут)

### 1. Загрузите на GitHub (3 минуты)

```bash
# Подготовка
chmod +x prepare-github.sh
./prepare-github.sh

# Создайте репозиторий на https://github.com/new
# Название: tender-finder

# Добавьте remote (ЗАМЕНИТЕ YOUR_USERNAME!)
git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git

# Push
git push -u origin main
```

### 2. Деплой на Railway (7 минут)

1. **Зайдите на [railway.app](https://railway.app)** (регистрация через GitHub)

2. **New Project** → **Deploy from GitHub repo** → Выберите `tender-finder`

3. **Настройте Backend сервис:**
   - Нажмите на сервис → Settings
   - **Root Directory:** `backend`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Variables → Add Variable:
     ```
     DATABASE_PATH=./goszakup_lots.db
     ```

4. **Добавьте Frontend сервис:**
   - New → GitHub Repo → tender-finder
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Start Command:** `npm run preview -- --host 0.0.0.0 --port $PORT`
   - Variables → Add Variable:
     ```
     VITE_API_URL=https://tender-finder-backend.up.railway.app
     ```
     (Скопируйте URL из Backend сервиса)

5. **Дождитесь деплоя** (3-5 минут)

**✅ Готово! Ваше приложение онлайн!**

---

## 🧪 ШАГ 3: Тестирование

### Локально:
```bash
# Health check
curl http://localhost:8000/health

# Получить статистику
curl http://localhost:8000/stats
```

### На Railway:
```bash
# Замените на ваш URL
curl https://tender-finder-backend.up.railway.app/health
```

---

## 🎨 Что можно делать

### 💰 Поиск по бюджету
Введите **700,000₸** → Найдёт лоты с себестоимостью 560К-840К₸

### 📈 Поиск по марже
Введите **1,500,000₸** → Найдёт лоты с прибылью 1.2М-1.8М₸

### 📦 Каталог
- Поиск по названию
- Фильтр по категориям
- Просмотр деталей
- Расчёт прибыли

---

## 🐛 Проблемы?

### Backend не запускается:
```bash
cd backend
pip install --upgrade -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend не запускается:
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Railway деплой не работает:
```bash
# Проверьте логи
railway logs

# Перезапуск
railway restart
```

---

## 📚 Полная документация

- **Установка:** [SETUP.md](./SETUP.md)
- **Деплой:** [DEPLOY.md](./DEPLOY.md)
- **API:** [README.md](./README.md)

---

## 🎯 Структура проекта

```
tender-finder-app/
├── backend/                 # FastAPI сервер
│   ├── main.py             # API endpoints
│   ├── requirements.txt    # Python зависимости
│   └── goszakup_lots.db    # База данных (99 лотов)
│
├── frontend/                # React приложение
│   ├── src/
│   │   ├── App.jsx         # Главный компонент
│   │   ├── main.jsx        # Entry point
│   │   └── index.css       # Tailwind стили
│   └── package.json        # Node зависимости
│
├── start.sh                 # Запуск (Linux/Mac)
├── start.bat                # Запуск (Windows)
├── prepare-github.sh        # Подготовка к GitHub
└── README.md                # Документация
```

---

## ⚡ Команды для копипасты

### Локальный запуск:
```bash
./start.sh           # Linux/Mac
start.bat            # Windows
```

### Подготовка к GitHub:
```bash
./prepare-github.sh
git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git
git push -u origin main
```

### Проверка API:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats
curl http://localhost:8000/lots?limit=5
```

### Поиск по бюджету:
```bash
curl -X POST http://localhost:8000/lots/search-by-budget \
  -H "Content-Type: application/json" \
  -d '{"budget": 700000}'
```

---

**🎉 ВСЁ! Теперь у вас работающее приложение!**

**⭐ Поставьте звезду на GitHub если понравилось!**
