#!/bin/bash
echo "Starting Trading Workstation..."

# Cleanup existing processes
echo "Cleaning up existing processes on ports 8000 and 5173..."
kill $(lsof -t -i :8000) 2>/dev/null || true
kill $(lsof -t -i :5173) 2>/dev/null || true
sleep 2

# 1. Start Backend
echo "Launching Backend..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# 2. Start Frontend
echo "Launching Frontend..."
cd ../frontend
# Force vite to use 5173 or exit
npm run dev -- --host 0.0.0.0 --port 5173 --strictPort > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "------------------------------------------------"
echo "Workstation is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Logs: backend.log, frontend.log"
echo "------------------------------------------------"
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C to kill background processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
