# ⚡ ШПАРГАЛКА: Railway настройки

## 🔴 BACKEND СЕРВИС

```
Root Directory:       backend
Start Command:        uvicorn main:app --host 0.0.0.0 --port $PORT
Build Command:        (пусто)

Variables:
  DATABASE_PATH = ./goszakup_lots.db
```

---

## 🔵 FRONTEND СЕРВИС

```
Root Directory:       frontend
Build Command:        npm run build
Start Command:        npm run preview -- --host 0.0.0.0 --port $PORT

Variables:
  VITE_API_URL = https://[ваш-backend-url].railway.app
  (БЕЗ слэша в конце!)
```

---

## 📝 КОПИПАСТА ДЛЯ RAILWAY UI

### Backend Start Command:
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Frontend Build Command:
```
npm run build
```

### Frontend Start Command:
```
npm run preview -- --host 0.0.0.0 --port $PORT
```

---

## ⚠️ ВАЖНО!

1. Создать **2 отдельных сервиса** из одного репозитория
2. Backend **БЕЗ** Build Command
3. Frontend **С** Build Command
4. VITE_API_URL **БЕЗ** слэша в конце

---

## 🔄 ПОРЯДОК ДЕЙСТВИЙ:

```
1. Deploy backend → дождаться успешного деплоя
2. Скопировать backend URL
3. Deploy frontend с VITE_API_URL = backend URL
4. Готово!
```

---

**Полная инструкция: RAILWAY_DEPLOY.md**
