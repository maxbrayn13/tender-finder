# 🏆 TenderFinder - Flask Edition

**Платформа для поиска выгодных госзакупок Казахстана**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Flask](https://img.shields.io/badge/flask-3.0-green)
![Railway](https://img.shields.io/badge/railway-ready-green)

---

## ✨ Flask Edition - Почему?

**FastAPI версия не работала на Railway из-за pydantic-core (компиляция Rust)**

**Flask версия работает 100%:**
- ✅ Простые зависимости (Flask, gunicorn)
- ✅ Быстрая установка
- ✅ Нет компиляции
- ✅ Как tender-watch

---

## 🚀 Быстрый деплой (10 минут)

### 1. Загрузить на GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/maxbrayn13/tender-finder.git
git push -u origin main
```

### 2. Деплой на Railway
```
1. Railway.app → New Project
2. Deploy from GitHub repo
3. Выбрать tender-finder
4. ГОТОВО! Ждать 5 минут
```

**Подробная инструкция:** `RAILWAY_DEPLOY.md`

---

## 🎯 Возможности

- 💰 **Поиск по бюджету** - найдите лоты под ваш бюджет
- 📈 **Поиск по марже** - найдите лоты с нужной прибылью
- 📊 **Автоматический расчёт** - ROI, маржа, себестоимость
- 🔍 **Каталог** - 99 реальных лотов из goszakup.gov.kz
- 📱 **Responsive** - работает на всех устройствах

---

## 🛠 Технологии

### Backend:
- Flask 3.0.0
- SQLite (99 лотов)
- Gunicorn 21.2.0
- Flask-CORS 4.0.0

### Frontend:
- Vanilla JavaScript
- Tailwind CSS (CDN)
- Single Page Application

---

## 📁 Структура

```
tender-finder-flask/
├── app.py               # Flask backend
├── Procfile             # Railway конфигурация
├── requirements.txt     # Python зависимости
├── goszakup_lots.db     # База данных (99 лотов)
├── static/
│   └── index.html       # Frontend SPA
└── .gitignore
```

---

## 💻 Локальный запуск

```bash
# Установить зависимости
pip install -r requirements.txt

# Запустить
python app.py

# Открыть
http://localhost:5000
```

---

## 📊 API Endpoints

- `GET /api` - API info
- `GET /api/health` - Health check
- `GET /api/lots` - Список лотов
- `GET /api/lots/{id}` - Лот по ID
- `POST /api/lots/search` - Поиск
- `POST /api/lots/search-by-budget` - 💰 Поиск по бюджету
- `POST /api/lots/search-by-margin` - 📈 Поиск по марже
- `GET /api/stats` - Статистика
- `GET /api/categories` - Категории

---

## 🗄️ База данных

**Файл:** `goszakup_lots.db`
**Лотов:** 99
**Категорий:** 7

---

## 🎨 Дизайн

- Анимированный градиент фон
- Glassmorphism эффекты
- Адаптивная вёрстка
- Tailwind CSS

---

## 📈 Roadmap

- [x] Backend API (Flask)
- [x] Frontend SPA
- [x] Railway деплой
- [ ] Аутентификация
- [ ] Email уведомления
- [ ] Telegram бот

---

## 🔧 Flask vs FastAPI

| Параметр | FastAPI | Flask |
|----------|---------|-------|
| Зависимости | pydantic (Rust) | Чистый Python |
| Установка | ❌ Ошибка | ✅ Работает |
| Документация | Автоматическая | Вручную |
| Простота | Средняя | Высокая |
| Railway | ❌ Проблемы | ✅ 100% |

**Вывод:** Для Railway лучше Flask!

---

## 📄 Лицензия

MIT License - можно использовать коммерчески

---

## 🎉 Готово!

**Читайте `RAILWAY_DEPLOY.md` для деплоя!**

---

**Сделано с ❤️ для тендерных специалистов Казахстана**

**Flask = Простота = Надёжность!** ✅