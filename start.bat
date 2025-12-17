@echo off
echo 🚀 Запуск TenderFinder локально...

REM Backend
echo 📦 Запуск Backend...
cd backend
if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
start "Backend" cmd /k uvicorn main:app --reload --port 8000
cd ..

REM Frontend
echo 📦 Запуск Frontend...
cd frontend
if not exist node_modules (
    echo Установка зависимостей...
    call npm install
)
start "Frontend" cmd /k npm run dev
cd ..

echo.
echo ✅ TenderFinder запущен!
echo 📊 Backend: http://localhost:8000
echo 🖥️  Frontend: http://localhost:3000
echo 📚 API Docs: http://localhost:8000/docs
echo.
pause
