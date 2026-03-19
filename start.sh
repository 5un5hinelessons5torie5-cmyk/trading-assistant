#!/bin/bash
echo "🚀 Starting Trading Workstation..."

# 1. Kill any existing processes on ports 8000 (Backend) and 5173 (Frontend)
echo "🧹 Cleaning up existing processes..."
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null
sleep 2

# 2. Start Backend in background
echo "📦 Launching Backend (FastAPI)..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# 3. Start Frontend in background
echo "💻 Launching Frontend (Vite)..."
cd ../frontend
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# 4. Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
for i in {1..10}; do
    if curl -s http://localhost:8000/ > /dev/null && curl -s http://localhost:5173/ > /dev/null; then
        break
    fi
    sleep 2
done

# Final check
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend is ONLINE: http://localhost:8000"
else
    echo "❌ Backend FAILED to start. Check backend.log"
fi

if curl -s http://localhost:5173/ > /dev/null; then
    echo "✅ Frontend is ONLINE: http://localhost:5173"
else
    echo "❌ Frontend FAILED to start. Check frontend.log"
fi

echo "------------------------------------------------"
echo "Workstation is active!"
echo "Press Ctrl+C to shut down all services."
echo "------------------------------------------------"

# Trap Ctrl+C to kill both services
trap "echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
