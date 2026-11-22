@echo off
title AromaLuxe Perfumes - Servidor Web
color 0A
echo ==============================================================
echo           AROMALUXE - PERFUMERIA & CATALOGO ESTILO FRAGRANTICA
echo ==============================================================
echo.
echo Iniciando servidor web con Python Flask...
echo.
echo [1] Para acceder desde esta PC:
echo     http://127.0.0.1:5000
echo.
echo [2] Para acceder desde tu CELULAR (misma red Wi-Fi):
echo     http://192.168.15.3:5000
echo.
echo [3] Panel de Administrador (para gestionar stock y perfumes):
echo     http://192.168.15.3:5000/admin
echo     PIN por defecto: 1234
echo.
echo Presiona Ctrl + C en esta ventana para detener el servidor.
echo ==============================================================
echo.
python app.py
pause
