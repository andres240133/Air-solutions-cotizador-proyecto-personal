@echo off
title AirSolutions - Sistema de Cotizaciones
color 0A
echo.
echo ========================================
echo   AIRSOLUTIONS
echo   Sistema de Cotizaciones HVAC
echo ========================================
echo.

cd /d "%~dp0"

REM Intentar con python en PATH
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo Iniciando con Python...
    python main.py
    goto :end
)

REM Intentar con ruta común de Python
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" (
    echo Iniciando con Python 3.13...
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe" main.py
    goto :end
)

REM Intentar con py launcher
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Iniciando con py launcher...
    py main.py
    goto :end
)

REM Si no encuentra Python
echo.
echo [ERROR] No se encuentra Python instalado
echo.
echo Por favor instala Python 3.13 desde python.org
echo.
pause
exit /b 1

:end
echo.
pause
