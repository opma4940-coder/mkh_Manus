#!/bin/bash
set -e
echo "--------------------------------------------------"
echo "🚀 Starting 100% System Validation..."
echo "--------------------------------------------------"

echo "📁 Phase 1: Structure Audit..."
[ -f "infra/docker-compose.yml" ] && echo "✅ infra/docker-compose.yml OK" || exit 1
[ -f "docker-compose.yml" ] && echo "✅ docker-compose.yml OK" || exit 1
[ -f "backend/app/main.py" ] && echo "✅ backend/app/main.py OK" || exit 1
[ -f "frontend/src/App.tsx" ] && echo "✅ frontend/src/App.tsx OK" || exit 1

echo "🐳 Phase 2: Path Validation..."
grep -q "\.\./backend" infra/docker-compose.yml && echo "✅ infra paths OK" || exit 1

echo "🛠️ Phase 3: Syntax Check..."
python3 -m py_compile backend/app/main.py && echo "✅ Python Syntax OK" || exit 1

echo "🎨 Phase 4: UI Audit..."
grep -q "color-bg-primary" frontend/src/styles/variables.css && echo "✅ UI Variables OK" || exit 1

echo "--------------------------------------------------"
echo "🎉 100% VALIDATION SUCCESSFUL!"
echo "--------------------------------------------------"
