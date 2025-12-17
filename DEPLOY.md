# 🚀 ДЕПЛОЙ НА RAILWAY - ИСПРАВЛЕННАЯ ИНСТРУКЦИЯ

⚠️ **ВАЖНО:** Railway требует создания 2 отдельных сервисов (Backend + Frontend)

---

## Шаг 1: Загрузка на GitHub

```bash
# Инициализация Git
git init
git add .
git commit -m "🎉 Initial commit: TenderFinder v1.0"

# Создайте репозиторий на github.com
# Затем:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git
git push -u origin main
```

---

## Шаг 2: Деплой на Railway

### Метод 1: Через интерфейс Railway (проще)

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Авторизуйте GitHub и выберите репозиторий `tender-finder`

#### Backend сервис:
- **Root Directory**: `backend`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  ```
  DATABASE_PATH=./goszakup_lots.db
  ```

#### Frontend сервис:
- Добавьте второй сервис в том же проекте
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`
- **Environment Variables**:
  ```
  VITE_API_URL=https://[ваш-backend].railway.app
  ```

5. Нажмите **Deploy** и ждите 3-5 минут

---

### Метод 2: Через Railway CLI (для продвинутых)

```bash
# Установка CLI
npm install -g @railway/cli

# Логин
railway login

# Инициализация
railway init

# Создание Backend
railway service create backend
railway service --service backend
railway up

# Создание Frontend
railway service create frontend
railway service --service frontend
railway up

# Установка переменных
railway variables set DATABASE_PATH=./goszakup_lots.db --service backend
railway variables set VITE_API_URL=https://your-backend.railway.app --service frontend
```

---

## Шаг 3: Проверка

После деплоя вы получите 2 URL:
- **Backend**: `https://tender-finder-backend.railway.app`
- **Frontend**: `https://tender-finder-frontend.railway.app`

Проверьте:
```bash
curl https://tender-finder-backend.railway.app/health
# Ответ: {"status":"healthy","timestamp":"..."}
```

Откройте frontend URL в браузере!

---

## 🔄 Обновление приложения

После изменений в коде:

```bash
git add .
git commit -m "✨ Update: описание изменений"
git push
```

Railway автоматически перезагрузит приложение!

---

## ⚠️ Важные моменты

1. **База данных**: В продакшене база SQLite не сохраняется между деплоями. Рассмотрите переход на PostgreSQL:
   ```bash
   railway add --database postgres
   ```

2. **CORS**: Обновите список разрешённых доменов в `backend/main.py`:
   ```python
   allow_origins=[
       "https://your-frontend.railway.app",
       "http://localhost:3000"
   ]
   ```

3. **API URL**: Обновите в frontend переменную `VITE_API_URL` на реальный URL backend

---

## 🆘 Помощь

**Логи Railway:**
```bash
railway logs --service backend
railway logs --service frontend
```

**Перезапуск:**
```bash
railway service --service backend
railway restart
```

---

**Готово! 🎉 Ваше приложение онлайн!**
