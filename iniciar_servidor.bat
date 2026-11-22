@echo off
title The Fragance´s - Servidor Web
color 0A
echo ==============================================================
echo           THE FRAGANCE´S - ALTA PERFUMERIA & CATALOGO
echo ==============================================================
echo.

:: 1. Intentar detectar Python en PATH
set "PY_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :INICIAR
)

:: 2. Intentar con el lanzador oficial de Windows 'py'
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :INICIAR
)

:: 3. Buscar en rutas estándar de instalación de Windows
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :INICIAR
    )
)

for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :INICIAR
    )
)

for /d %%D in ("%PROGRAMFILES%\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :INICIAR
    )
)

:: 4. Si no se encontró en ninguna parte:
color 0C
echo [ERROR] No se detecto Python instalado en el sistema.
echo.
echo Para solucionarlo rapidamente:
echo   1. Vuelve a abrir el instalador de Python (o descargalo de python.org).
echo   2. Marca la casilla "Add python.exe to PATH" abajo antes de instalar.
echo   3. Vuelve a ejecutar este archivo.
echo ==============================================================
echo.
pause
exit /b 1

:INICIAR
echo [OK] Python detectado: %PY_CMD%
echo.
echo Iniciando servidor web de The Fragance´s...
echo.
echo [1] Para acceder desde esta PC:
echo     http://127.0.0.1:5000
echo.
echo [2] Panel de Administrador (para gestionar stock y resenas):
echo     http://127.0.0.1:5000/login
echo     Usuario: admin@thefragances.com
echo     Clave: admin (o PIN: 1234)
echo.
echo Presiona Ctrl + C en esta ventana para detener el servidor.
echo ==============================================================
echo.
%PY_CMD% app.py
pause
