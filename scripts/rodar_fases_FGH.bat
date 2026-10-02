@echo off
REM ==========================================================================
REM  rodar_fases_FGH.bat  -  coletas das fases F, G e H (precisam de internet)
REM  Pode fechar esta janela so quando aparecer "TUDO PRONTO".
REM ==========================================================================
chcp 65001 >nul
cd /d "%~dp0.."
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
if not exist dados\execucao mkdir dados\execucao
echo INICIO %date% %time%> dados\execucao\status.txt

echo [1/5] Modelos de linguagem (FinBERT-PT-BR e distilbert) em paralelo...
start "InvestAI - modelos" /min cmd /c "venv\Scripts\python.exe -u scripts\30_sentimento_modelos.py > dados\execucao\log_30_modelos.txt 2>&1"

echo [2/5] Barras de 1 e 5 minutos do Yahoo...
venv\Scripts\python.exe -u scripts\31_baixar_minuto.py > dados\execucao\log_31_minuto.txt 2>&1

echo [3/5] Noticias recentes + horarios WordPress...
venv\Scripts\python.exe -u scripts\32_coletar_recentes.py > dados\execucao\log_32_recentes.txt 2>&1

echo [4/5] Small caps: carteira da B3, sondagem, sorteio e coleta...
venv\Scripts\python.exe -u scripts\33_smallcaps.py > dados\execucao\log_33_smallcaps.txt 2>&1

echo Esperando os modelos terminarem...
:espera
findstr /c:"FIM_30" dados\execucao\status.txt >nul 2>&1
if errorlevel 1 (
    timeout /t 20 /nobreak >nul
    goto espera
)

echo [5/5] Modelos nas manchetes novas (recentes e small caps)...
venv\Scripts\python.exe -u scripts\30_sentimento_modelos.py > dados\execucao\log_30b_modelos.txt 2>&1
echo FIM_TUDO %date% %time%>> dados\execucao\status.txt
echo.
echo TUDO PRONTO. Pode fechar esta janela.
