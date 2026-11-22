@echo off
cd /d "%~dp0"
chcp 65001 >nul
title The Fragances - Servidor Web
color 0A

echo ==============================================================
echo           THE FRAGANCES - ALTA PERFUMERIA Y CATALOGO
echo ==============================================================
echo.

REM 1. Buscar comando de Python
set "PY_CMD="

python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
    goto :ENCONTRADO
)

py --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py"
    goto :ENCONTRADO
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :ENCONTRADO
    )
)

for /d %%D in ("C:\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :ENCONTRADO
    )
)

for /d %%D in ("%PROGRAMFILES%\Python*") do (
    if exist "%%D\python.exe" (
        set "PY_CMD=%%D\python.exe"
        goto :ENCONTRADO
    )
)

:NO_ENCONTRADO
color 0C
echo [ERROR] No se pudo encontrar Python en tu computadora.
echo.
echo Para solucionarlo facilmente:
echo   1. Descarga Python desde: https://www.python.org/downloads/
echo   2. Abre el instalador y MARCA la casilla "Add python.exe to PATH".
echo   3. Vuelve a hacer doble clic en este archivo.
echo.
echo ==============================================================
pause
goto :EOF

:ENCONTRADO
echo [OK] Python detectado: %PY_CMD%
echo.

REM 2. Verificar libreria Flask
"%PY_CMD%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INSTALANDO LIBRERIAS] Flask no esta instalado aun.
    echo Descargando e instalando Flask automaticamente...
    echo.
    "%PY_CMD%" -m pip install -r requirements.txt
    if errorlevel 1 (
        color 0C
        echo.
        echo [ERROR] Hubo un problema al instalar las librerias.
        echo Verifica tu conexion a internet e intenta nuevamente.
        echo.
        pause
        goto :EOF
    )
    echo.
    echo [OK] Librerias instaladas con exito.
    echo.
)

REM 3. Iniciar la aplicacion web
echo ==============================================================
echo Iniciando servidor web de The Fragances...
echo.
echo [1] Abre tu navegador y entra a:
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
"%PY_CMD%" app.py

echo.
echo El servidor se ha detenido.
pause
