#!/bin/bash

# TenderFinder - Локальный запуск
echo "🚀 Запуск TenderFinder локально..."

# Проверка зависимостей
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 не установлен"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js не установлен"; exit 1; }

# Backend
echo "📦 Запуск Backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Frontend
echo "📦 Запуск Frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Установка зависимостей..."
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ TenderFinder запущен!"
echo "📊 Backend: http://localhost:8000"
echo "🖥️  Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Нажмите Ctrl+C для остановки..."

# Ожидание завершения
wait $BACKEND_PID $FRONTEND_PID
