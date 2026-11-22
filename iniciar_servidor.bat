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
    goto :VERIFICAR_LIBRERIAS
)

:: 2. Intentar con el lanzador oficial de Windows 'py'
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :VERIFICAR_LIBRERIAS
)

:: 3. Buscar en rutas estandar de instalacion de Windows
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :VERIFICAR_LIBRERIAS
    )
)

for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :VERIFICAR_LIBRERIAS
    )
)

for /d %%D in ("%PROGRAMFILES%\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :VERIFICAR_LIBRERIAS
    )
)

:: 4. Si no se encontro Python:
color 0C
echo [ERROR] No se detecto Python instalado en esta computadora.
echo.
echo Para solucionarlo:
echo   1. Descarga Python gratis desde: https://www.python.org/downloads/
echo   2. Al instalar, MARCA la casilla "Add python.exe to PATH".
echo   3. Vuelve a ejecutar este archivo.
echo ==============================================================
echo.
pause
exit /b 1

:VERIFICAR_LIBRERIAS
echo [OK] Python detectado: %PY_CMD%
echo.

:: Verificar si Flask esta instalado
%PY_CMD% -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INSTALACION AUTOMATICA] Flask no esta instalado aun.
    echo Instalando librerias necesarias (Flask, etc.)...
    echo.
    %PY_CMD% -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo [ERROR] Hubo un problema al instalar Flask.
        echo Verifica tu conexion a internet o ejecuta en la consola:
        echo   pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo.
    echo [OK] Librerias instaladas con exito.
    echo.
)

:INICIAR
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
