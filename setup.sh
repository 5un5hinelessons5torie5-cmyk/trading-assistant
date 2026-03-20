#!/bin/bash
echo "Installing Backend dependencies..."
cd backend
pip install -r requirements.txt

echo "Installing Frontend dependencies..."
cd ../frontend
npm install

echo "Setup complete!"
