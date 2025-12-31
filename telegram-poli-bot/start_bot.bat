@echo off
setlocal enabledelayedexpansion

REM Set UTF-8 encoding
chcp 65001 >nul

REM Set title
title Telegram Poli Bot - Auto Running

REM Set paths
set BOT_DIR=d:\Latihan Olah Data\Tools\BotTelegram\telegram-poli-bot
set LOG_FILE=%BOT_DIR%\bot_log.txt

REM Navigate to bot directory
cd /d "%BOT_DIR%"

:start_bot
REM Clear screen dan tampilkan info
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

REM Run bot dengan logging
python bot.py >> "%LOG_FILE%" 2>&1

REM Check exit code
if errorlevel 1 (
    echo.
    echo ========================================
    echo Bot crashed at %date% %time%
    echo Exit Code: %errorlevel%
    echo.
    echo Checking internet connection...
    ping -n 1 8.8.8.8 >nul 2>&1
    if errorlevel 1 (
        echo WARNING: No internet connection detected!
        echo Waiting 30 seconds before retry...
        timeout /t 30 /nobreak
    ) else (
        echo Internet connection OK
        echo Restarting in 10 seconds...
        timeout /t 10 /nobreak
    )
) else (
    echo Bot stopped normally
    timeout /t 10 /nobreak
)

REM Restart bot
goto start_bot

:end
endlocal
