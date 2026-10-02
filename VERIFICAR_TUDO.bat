@echo off
REM ==========================================================================
REM  VERIFICAR_TUDO.bat - refaz TODOS os testes do estudo a partir dos dados
REM  congelados e confere se os resultados saem iguais aos publicados.
REM  Nao precisa de internet. Leva de 10 a 60 minutos, conforme o computador.
REM  Pode fechar esta janela quando aparecer "Relatorio salvo".
REM ==========================================================================
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set PY=python
if exist venv\Scripts\python.exe set PY=venv\Scripts\python.exe
echo Verificando o estudo InvestAI com %PY% ...
echo.
%PY% -u verificacao\verificar_tudo.py
echo.
echo Relatorio salvo em verificacao\relatorio_verificacao.txt
echo FIM_VERIFICACAO %date% %time%> verificacao\status_verificacao.txt
pause
