@echo off
cd /d "%~dp0"
chcp 65001 >nul
title Instalar Dependencias - The Fragances
color 0B

echo ==============================================================
echo       INSTALADOR DE LIBRERIAS - THE FRAGANCES PERFUMES
echo ==============================================================
echo.

set "PY_CMD="

python --version >nul 2>&1
if not errorlevel 1 set "PY_CMD=python"

if not defined PY_CMD (
    py --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=py"
)

if not defined PY_CMD (
    for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%D\python.exe" set "PY_CMD=%%D\python.exe"
    )
)

if not defined PY_CMD (
    for /d %%D in ("C:\Python*") do (
        if exist "%%D\python.exe" set "PY_CMD=%%D\python.exe"
    )
)

if not defined PY_CMD (
    color 0C
    echo [ERROR] No se encontro Python en el equipo.
    echo Descargalo gratis desde: https://www.python.org/downloads/
    echo Recuerda marcar la casilla "Add python.exe to PATH".
    echo.
    pause
    goto :EOF
)

echo [OK] Usando: %PY_CMD%
echo.
echo Instalando Flask y librerias del proyecto...
echo.
"%PY_CMD%" -m pip install -r requirements.txt

if not errorlevel 1 (
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
    echo Verifica tu conexion a internet e intenta nuevamente.
)

echo.
pause
