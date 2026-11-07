@echo off
chcp 65001 >nul
echo ==============================================
echo 🛑 Зупинка фонового процесу OLX Deal Sniper...
echo ==============================================
wmic process where "commandline like '%%olxparcer%%'" delete 2>nul
if %errorlevel% neq 0 (
    taskkill /F /FI "WINDOWTITLE eq olx-sniper*" 2>nul
)
echo.
echo ✅ Сервіс успішно зупинено.
echo.
pause
