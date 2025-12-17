#!/bin/bash

# Подготовка проекта TenderFinder для публикации на GitHub

echo "🚀 Подготовка TenderFinder к публикации..."

# Проверка git
if ! command -v git &> /dev/null; then
    echo "❌ Git не установлен. Установите: https://git-scm.com"
    exit 1
fi

# Инициализация git (если нужно)
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    git branch -M main
fi

# Создание .gitignore если нет
if [ ! -f ".gitignore" ]; then
    echo "📝 Создание .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
venv/
*.egg-info/

# Node
node_modules/
dist/
*.local

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database journals
*.db-journal
EOF
fi

# Добавление всех файлов
echo "📥 Добавление файлов..."
git add .

# Commit
echo "💾 Создание commit..."
read -p "Введите сообщение commit (или нажмите Enter для 'Initial commit'): " commit_msg
commit_msg=${commit_msg:-"🎉 Initial commit: TenderFinder v1.0

- FastAPI backend с SQLite
- React frontend с Tailwind CSS
- 2 умных калькулятора (бюджет/маржа)
- API для поиска лотов
- Готово к деплою на Railway"}

git commit -m "$commit_msg"

echo ""
echo "✅ Проект готов к публикации!"
echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1️⃣ Создайте репозиторий на GitHub:"
echo "   https://github.com/new"
echo ""
echo "2️⃣ Добавьте remote (замените YOUR_USERNAME):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/tender-finder.git"
echo ""
echo "3️⃣ Push на GitHub:"
echo "   git push -u origin main"
echo ""
echo "4️⃣ Деплой на Railway:"
echo "   - Зайдите на https://railway.app"
echo "   - New Project → Deploy from GitHub repo"
echo "   - Выберите ваш репозиторий"
echo ""
echo "🎉 Готово! Удачи!"
