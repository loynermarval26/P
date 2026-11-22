@echo off
title Instalar Dependencias - The Fragance´s
color 0B
echo ==============================================================
echo       INSTALADOR DE LIBRERIAS - THE FRAGANCE´S PERFUMES
echo ==============================================================
echo.

set "PY_CMD="
python --version >nul 2>&1
if %errorlevel% equ 0 set "PY_CMD=python"
if not defined PY_CMD (
    py --version >nul 2>&1
    if %errorlevel% equ 0 set "PY_CMD=py"
)
if not defined PY_CMD (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PY_CMD=%%D\python.exe"
    )
)

if not defined PY_CMD (
    color 0C
    echo [ERROR] No se encontro Python. Descargalo de https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Usando: %PY_CMD%
echo.
echo Instalando Flask y librerias del proyecto...
%PY_CMD% -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    color 0A
    echo.
    echo ==============================================================
    echo [EXITO] Todas las librerias fueron instaladas correctamente.
    echo Ya puedes abrir "iniciar_servidor.bat" para iniciar la web.
    echo ==============================================================
) else (
    color 0C
    echo.
    echo [ERROR] Ocurrio un fallo al instalar las dependencias.
)
echo.
pause
