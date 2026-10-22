#!/usr/bin/env bash
# ==============================================================================
# SafeStack AI - 1-Click Launch Script
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================================="
echo "  🛡️  SafeStack AI: Real-Time Damage-Free Warehouse Intelligence  "
echo "=================================================================="
echo ""

# Check Python environment
if [ -f "./backend/.venv/bin/python" ]; then
    PYTHON_CMD="./backend/.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

echo "✅ Using Python: $($PYTHON_CMD --version)"

# Check Node environment
if command -v node &>/dev/null; then
    echo "✅ Using Node: $(node -v)"
else
    echo "⚠️ Node.js not detected. The backend will serve the pre-built frontend distribution on port 8000."
fi

# Run pytest verification
echo "🧪 Running unit & integration tests..."
PYTHONPATH=. $PYTHON_CMD -m pytest backend/tests -q || true

# Start backend
echo "🚀 Starting SafeStack AI Backend on http://localhost:8000..."
PYTHONPATH=. $PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Trap signals to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down SafeStack AI services..."
    kill $BACKEND_PID 2>/dev/null || true
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Start frontend dev server if npm is present, or serve via backend
if command -v npm &>/dev/null && [ -d "./frontend/node_modules" ]; then
    echo "⚡ Starting Vite Frontend on http://localhost:5173..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo ""
    echo "🌐 Dashboard Ready at: http://localhost:5173"
    echo "📡 API & Swagger Docs: http://localhost:8000/docs"
else
    echo ""
    echo "🌐 Dashboard Ready at: http://localhost:8000"
    echo "📡 API & Swagger Docs: http://localhost:8000/docs"
fi

echo ""
echo "Press [Ctrl+C] to stop all services."
wait
