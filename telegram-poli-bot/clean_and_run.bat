@echo off
setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul

REM Set title
title Telegram Poli Bot - Cleaning & Running

REM Set paths
set BOT_DIR=d:\Latihan Olah Data\Tools\BotTelegram\telegram-poli-bot
set LOG_FILE=%BOT_DIR%\bot_log.txt

REM Navigate to bot directory
cd /d "%BOT_DIR%"

REM Clean cache
echo Cleaning cache...
if exist __pycache__ (
    rmdir /s /q __pycache__
    echo Cache cleaned
)

REM Delete .pyc files
for /r . %%f in (*.pyc) do del "%%f"

REM Delete old log
if exist "%LOG_FILE%" (
    del "%LOG_FILE%"
    echo Old log deleted
)

echo.
echo Starting bot...
echo.

:start_bot
cls
echo.
echo ========================================
echo   TELEGRAM POLI BOT
echo ========================================
echo.
echo Status: RUNNING
echo Time: %date% %time%
echo Directory: %cd%
echo Log: %LOG_FILE%
echo.
echo Press Ctrl+C to stop bot
echo ========================================
echo.

REM Run bot
python bot.py >> "%LOG_FILE%" 2>&1

REM If bot stops
echo.
echo ========================================
echo Bot stopped at %date% %time%
echo Restarting in 10 seconds...
echo ========================================
echo.

timeout /t 10 /nobreak

goto start_bot

:end
endlocal
