# 🚀 ПОЛНАЯ ИНСТРУКЦИЯ ПО ДЕПЛОЮ НА RAILWAY

## ✅ ЭТОТ АРХИВ ТОЧНО РАБОТАЕТ!

**Протестирована конфигурация с Gunicorn для надежного запуска**

---

## 📋 ШАГ 1: Загрузить на GitHub

### 1.1 Распаковать архив

```
tender-finder-working.zip → tender-finder-app/
```

### 1.2 Открыть PowerShell в папке

```powershell
cd путь\к\tender-finder-app
```

### 1.3 Инициализировать Git

```powershell
git init
git add .
git commit -m "Initial commit: TenderFinder"
git branch -M main
```

### 1.4 Создать репозиторий на GitHub

1. Зайти на https://github.com
2. Войти под аккаунтом **maxbrayn13**
3. Нажать **+** → **New repository**
4. Название: `tender-finder`
5. Public ✓
6. **Create repository**

### 1.5 Push на GitHub

```powershell
git remote add origin https://github.com/maxbrayn13/tender-finder.git
git push -u origin main
```

**Ввести:**
```
Username: maxbrayn13
Password: [ваш токен]
```

---

## 🚂 ШАГ 2: Настроить Railway

### 2.1 Создать Backend сервис

**1. Зайти на https://railway.app**

**2. New Project → Deploy from GitHub repo → tender-finder**

**3. Settings:**

```
Root Directory:  backend

Start Command:
python -m gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

Variables:
DATABASE_PATH = ./goszakup_lots.db
```

**4. Deploy (подождать 3-5 минут)**

**5. Скопировать Backend URL:**
```
Settings → Domains → Public Domain
Например: https://tender-finder-backend-xxx.railway.app
```

---

### 2.2 Создать Frontend сервис

**1. В том же проекте: + New → GitHub Repo → tender-finder**

**2. Settings:**

```
Root Directory:  frontend

Build Command:
npm run build

Start Command:
npm run preview -- --host 0.0.0.0 --port $PORT

Variables:
VITE_API_URL = [ВСТАВИТЬ URL BACKEND]
Например: https://tender-finder-backend-xxx.railway.app
```

**(БЕЗ слэша в конце!)**

**3. Deploy (подождать 5-7 минут)**

---

## ✅ ШАГ 3: Проверить

### Backend:
```
https://[ваш-backend].railway.app

Должно показать:
{
  "message": "TenderFinder API v1.0",
  "docs": "/docs"
}
```

### Frontend:
```
https://[ваш-frontend].railway.app

Должно показать сайт TenderFinder
```

---

## 🎯 КРИТИЧЕСКИ ВАЖНО!

### Backend Start Command:
```
python -m gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

**Именно эта команда работает на 100%!**

**Не используйте:**
- ❌ `uvicorn main:app --host 0.0.0.0 --port $PORT`
- ❌ `cd backend && ...`
- ❌ Любые другие варианты

---

## 📊 СТРУКТУРА ПРОЕКТА

```
tender-finder-app/
├── backend/
│   ├── main.py              (FastAPI с __main__)
│   ├── requirements.txt     (с gunicorn!)
│   └── goszakup_lots.db     (99 лотов)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js       (с PORT из env)
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── .gitignore
```

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### Ошибка: "$PORT is not a valid integer"
**Решение:** Используйте команду с Gunicorn (указана выше)

### Ошибка: "uvicorn: command not found"
**Решение:** Проверьте Root Directory = `backend`

### Ошибка: "npm: command not found"
**Решение:** Проверьте Root Directory = `frontend`

### Frontend показывает, но API не работает
**Решение:** Проверьте VITE_API_URL (БЕЗ слэша в конце!)

---

## 🎉 ГОТОВО!

**Ваше приложение работает онлайн!**

- Backend API: https://[backend].railway.app
- Frontend: https://[frontend].railway.app

**Покажите друзьям! 🚀**

---

## 📞 ПОДДЕРЖКА

**Если что-то не работает:**
1. Проверьте логи: Deployments → View logs
2. Убедитесь Root Directory правильный
3. Проверьте Start Command (скопируйте точно!)
4. Проверьте переменные окружения

---

**© 2025 TenderFinder | Made with ❤️ for Kazakhstan tenders**
