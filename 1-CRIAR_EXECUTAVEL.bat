@echo off
chcp 65001 >nul
title Criar Executável - Dashboard Financeiro
color 0B

echo ============================================================
echo        📦 CRIAR EXECUTÁVEL DO DASHBOARD FINANCEIRO
echo ============================================================
echo.
echo Este processo irá:
echo   1. Instalar PyInstaller (se necessário)
echo   2. Compilar o dashboard em um executável
echo   3. Criar pasta pronta para distribuição
echo.
echo ⏱️  Tempo estimado: 3-5 minutos
echo.
pause

python criar_executavel.py

echo.
echo ============================================================
echo.
pause

