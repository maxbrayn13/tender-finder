# 🏆 TenderFinder - Платформа для поиска выгодных госзакупок

![TenderFinder](https://img.shields.io/badge/TenderFinder-v1.0-violet)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![React](https://img.shields.io/badge/React-18-blue)

**TenderFinder** — это платформа для поиска товаров из госзакупок Казахстана с автоматическим сравнением цен на маркетплейсах (Kaspi, 1688, Alibaba и др.).

---

## ✨ Возможности

### 🎯 Умный поиск
- **По бюджету** — найти лоты под вашу сумму инвестиций (±20%)
- **По марже** — найти лоты с желаемой чистой прибылью (±20%)
- **По категориям** — фильтрация по типам товаров
- **Живой поиск** — поиск по названию и номеру лота

### 💰 Аналитика
- Автоматический расчёт себестоимости
- Расчёт чистой прибыли
- ROI в процентах
- Сравнение цен с разных площадок

### 📊 Статистика
- Общее количество лотов
- Общая сумма тендеров
- Средняя маржа
- Количество "горячих" сделок (маржа >100%)

---

## 🚀 Быстрый старт

### Локальная разработка

#### 1️⃣ Клонируйте репозиторий
```bash
git clone https://github.com/YOUR_USERNAME/tender-finder.git
cd tender-finder
```

#### 2️⃣ Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend будет доступен на `http://localhost:8000`
API документация: `http://localhost:8000/docs`

#### 3️⃣ Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

Frontend будет доступен на `http://localhost:3000`

---

## 🌐 Деплой на Railway

### Вариант 1: Через Railway CLI (Рекомендуется)

#### 1️⃣ Установите Railway CLI
```bash
npm install -g @railway/cli
```

#### 2️⃣ Войдите в Railway
```bash
railway login
```

#### 3️⃣ Инициализируйте проект
```bash
cd tender-finder
railway init
```

#### 4️⃣ Создайте два сервиса

**Backend:**
```bash
# В корне проекта
railway up --service backend

# Установите переменные окружения
railway variables --service backend
# Добавьте:
# DATABASE_PATH=./goszakup_lots.db
# PORT=8000
```

**Frontend:**
```bash
railway up --service frontend

# Установите переменные
railway variables --service frontend
# Добавьте:
# VITE_API_URL=https://your-backend.railway.app
```

#### 5️⃣ Деплой
```bash
railway up
```

---

### Вариант 2: Через GitHub Integration

#### 1️⃣ Создайте репозиторий на GitHub
```bash
git init
git add .
git commit -m "Initial commit: TenderFinder v1.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git
git push -u origin main
```

#### 2️⃣ Подключите к Railway
1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий `tender-finder`

#### 3️⃣ Настройте Backend сервис
1. Railway автоматически определит Python проект
2. Установите **Root Directory**: `backend`
3. Добавьте **Environment Variables**:
   ```
   DATABASE_PATH=./goszakup_lots.db
   PORT=${{PORT}}
   ```
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 4️⃣ Настройте Frontend сервис
1. Добавьте новый сервис в том же проекте
2. Установите **Root Directory**: `frontend`
3. Добавьте **Environment Variables**:
   ```
   VITE_API_URL=https://your-backend-service.railway.app
   ```
4. **Build Command**: `npm run build`
5. **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

#### 5️⃣ Деплой
Railway автоматически начнёт деплой при push в GitHub!

---

## 📁 Структура проекта

```
tender-finder/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # Главный файл API
│   ├── requirements.txt        # Python зависимости
│   └── goszakup_lots.db        # SQLite база данных
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── App.jsx             # Главный компонент
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Tailwind CSS
│   ├── package.json            # Node.js зависимости
│   ├── vite.config.js          # Vite конфигурация
│   ├── tailwind.config.js      # Tailwind конфигурация
│   └── index.html              # HTML template
│
├── .gitignore                  # Git ignore rules
├── railway.json                # Railway конфигурация
├── Procfile                    # Railway start command
└── README.md                   # Этот файл
```

---

## 🔧 API Endpoints

### Основные endpoints

| Method | Endpoint | Описание |
|--------|----------|----------|
| `GET` | `/` | API информация |
| `GET` | `/health` | Health check |
| `GET` | `/lots` | Получить лоты |
| `GET` | `/lots/{id}` | Получить лот по ID |
| `POST` | `/lots/search` | Поиск лотов |
| `POST` | `/lots/search-by-budget` | Поиск по бюджету |
| `POST` | `/lots/search-by-margin` | Поиск по марже |
| `GET` | `/stats` | Общая статистика |
| `GET` | `/categories` | Список категорий |

### Примеры запросов

**Получить все лоты:**
```bash
curl http://localhost:8000/lots?limit=10
```

**Поиск по бюджету:**
```bash
curl -X POST http://localhost:8000/lots/search-by-budget \
  -H "Content-Type: application/json" \
  -d '{"budget": 700000, "delivery_percent": 15}'
```

**Поиск по марже:**
```bash
curl -X POST http://localhost:8000/lots/search-by-margin \
  -H "Content-Type: application/json" \
  -d '{"target_margin": 1500000, "delivery_percent": 15}'
```

**Получить статистику:**
```bash
curl http://localhost:8000/stats
```

---

## 🗄️ База данных

### Структура таблицы `lots`

| Колонка | Тип | Описание |
|---------|-----|----------|
| `id` | INTEGER | Primary Key |
| `announce_id` | TEXT | ID объявления |
| `lot_number` | TEXT | Номер лота |
| `original_name` | TEXT | Оригинальное название |
| `simplified_name` | TEXT | Упрощенное название |
| `chinese_name` | TEXT | Китайское название |
| `category` | TEXT | Категория товара |
| `tender_price` | REAL | Тендерная цена |
| `quantity` | INTEGER | Количество |
| `unit` | TEXT | Единица измерения |
| `customer` | TEXT | Заказчик |
| `is_service` | INTEGER | Услуга (0/1) |
| `suitable_for_china` | INTEGER | Подходит для Китая (0/1) |
| `created_at` | TEXT | Дата создания |
| `status` | TEXT | Статус |

---

## 🎨 Технологии

### Backend
- **FastAPI** — современный Python web framework
- **SQLite** — встроенная база данных
- **Pydantic** — валидация данных
- **Uvicorn** — ASGI сервер

### Frontend
- **React 18** — UI библиотека
- **Vite** — быстрый bundler
- **Tailwind CSS** — utility-first CSS framework
- **Fetch API** — HTTP клиент

### Деплой
- **Railway** — cloud platform
- **GitHub** — version control

---

## 🔐 Переменные окружения

### Backend (`.env`)
```bash
DATABASE_PATH=./goszakup_lots.db    # Путь к базе данных
PORT=8000                            # Порт сервера
```

### Frontend (`.env`)
```bash
VITE_API_URL=http://localhost:8000  # URL бэкенда
```

---

## 📊 Примеры использования

### Поиск по бюджету 700,000₸
```javascript
const response = await fetch('http://localhost:8000/lots/search-by-budget', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    budget: 700000,
    delivery_percent: 15
  })
});

const data = await response.json();
console.log(`Найдено ${data.total} лотов`);
```

### Поиск по марже 1,500,000₸
```javascript
const response = await fetch('http://localhost:8000/lots/search-by-margin', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_margin: 1500000,
    delivery_percent: 15
  })
});

const data = await response.json();
console.log(`Найдено ${data.total} лотов с прибылью ~1.5M₸`);
```

---

## 🐛 Troubleshooting

### Проблема: CORS ошибка
**Решение:** Проверьте что в `main.py` правильно настроен CORS:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Добавьте ваш frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Проблема: База данных не найдена
**Решение:** Убедитесь что файл `goszakup_lots.db` находится в папке `backend/`

### Проблема: Railway деплой не работает
**Решение:** 
1. Проверьте логи: `railway logs`
2. Убедитесь что `requirements.txt` корректен
3. Проверьте переменные окружения

---

## 📈 Roadmap

- [ ] Аутентификация пользователей
- [ ] Сохранение избранных лотов
- [ ] Email уведомления о новых лотах
- [ ] Интеграция реальных API маркетплейсов
- [ ] Автоматический парсинг новых лотов
- [ ] Экспорт в Excel
- [ ] Telegram бот
- [ ] Мобильное приложение

---

## 📄 Лицензия

MIT License - свободно используйте в коммерческих проектах

---

## 🤝 Контакты

- **GitHub**: [YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- **Email**: your.email@example.com

---

## ⭐ Понравился проект?

Поставьте звезду на GitHub! ⭐

---

**Сделано с ❤️ для тендерных специалистов Казахстана**
