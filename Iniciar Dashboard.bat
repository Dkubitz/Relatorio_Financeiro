@echo off
chcp 65001 >nul
title Dashboard Financeiro
color 0A

echo ============================================================
echo              📊 DASHBOARD FINANCEIRO 📊
echo ============================================================
echo.

:: Verificar se o arquivo CSV existe
if not exist "Fluxo Financeiro.csv" (
    color 0C
    echo ❌ ERRO: Arquivo "Fluxo Financeiro.csv" não encontrado!
    echo.
    echo    Certifique-se de que o arquivo CSV está nesta pasta.
    echo.
    pause
    exit /b 1
)

echo ✅ Arquivo CSV encontrado!
echo.
echo 🚀 Iniciando dashboard...
echo    (Aguarde alguns segundos, o navegador abrirá automaticamente)
echo.

:: Executar o launcher Python
python launcher.py

:: Se houver erro, mostrar mensagem
if errorlevel 1 (
    color 0C
    echo.
    echo ❌ Erro ao iniciar o dashboard.
    echo.
    echo 📋 Possíveis soluções:
    echo    1. Certifique-se de que o Python está instalado
    echo    2. Execute: pip install -r requirements.txt
    echo.
    pause
)

