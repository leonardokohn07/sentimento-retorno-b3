@echo off
REM Coleta diaria da Fase G (chamada pelo Agendador de Tarefas do Windows).
chcp 65001 >nul
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
venv\Scripts\python.exe -u scripts\34_coleta_diaria.py >> dados\prospectivo\saida_coleta_diaria.txt 2>&1
