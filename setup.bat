@echo off
echo 🚗⚡ Setting up ChargeX Agent...

echo [INFO] Installing backend dependencies...
cd backend
pip install -r requirements.txt
echo [SUCCESS] Backend dependencies installed!

cd ..
echo [INFO] Installing frontend dependencies...
npm install
echo [SUCCESS] Frontend dependencies installed!

echo [INFO] Creating startup scripts...

REM Create backend startup script
echo @echo off > start-backend.bat
echo echo 🔧 Starting ChargeX Agent Backend... >> start-backend.bat
echo cd backend >> start-backend.bat
echo python simple_main.py >> start-backend.bat

REM Create frontend startup script  
echo @echo off > start-frontend.bat
echo echo 🎨 Starting ChargeX Agent Frontend... >> start-frontend.bat
echo npm start >> start-frontend.bat

echo [SUCCESS] Setup complete! 🎉
echo.
echo 📋 Next Steps:
echo 1. Update backend\.env with your API keys
echo 2. Run start-backend.bat to launch backend
echo 3. Run start-frontend.bat to launch frontend
echo 4. Visit http://localhost:3000 to use ChargeX Agent
