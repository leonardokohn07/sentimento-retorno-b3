@echo off
REM ======================================================================
REM  ABRIR_PAINEL.bat  -  abre o painel do InvestAI com dois cliques
REM ======================================================================
REM  - Neste computador (venv ja existe): so liga o painel e abre o navegador.
REM  - Num computador novo: na primeira vez, cria o venv e instala as
REM    bibliotecas do requirements.txt (precisa de internet, alguns minutos).
REM
REM  O painel fica no ar enquanto esta janela estiver aberta.
REM  Para desligar, feche esta janela.
REM ======================================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title InvestAI - painel (feche esta janela para desligar)
set PYTHONIOENCODING=utf-8
set VP=venv\Scripts\python.exe
set ENDERECO=http://localhost:8501

if exist %VP% goto :conferir

REM ---------------------------------------------------------- primeira vez
echo.
echo  Primeira vez neste computador: preparando o ambiente do painel.
echo  Precisa de internet e leva alguns minutos. Aguarde...
echo.
set PY=
where py >nul 2>&1
if errorlevel 1 goto :sem_py
for %%v in (3.12 3.13 3.14 3.11) do if not defined PY py -%%v -c "import sys" >nul 2>&1 && set PY=py -%%v
:sem_py
if not defined PY python -c "import sys" >nul 2>&1 && set PY=python
if not defined PY goto :sem_python
%PY% -m venv venv
if not exist %VP% goto :sem_python
%VP% -m pip install --upgrade pip
%VP% -m pip install -r requirements.txt

REM ---------------------------------------------------------- bibliotecas
:conferir
%VP% -c "import streamlit, plotly, pandas, scipy" >nul 2>&1
if errorlevel 1 %VP% -m pip install -r requirements.txt

REM ---------------------------------------------------------- abrir
echo.
echo  ==============================================================
echo   Abrindo o painel do InvestAI no navegador...
echo   Endereco: %ENDERECO%
echo   Para desligar o painel, feche esta janela.
echo  ==============================================================
echo.
REM Abre o navegador assim que o painel responder (espera ate 60 s).
start "" powershell -NoProfile -WindowStyle Hidden -Command "for($i=0;$i -lt 120;$i++){try{$c=New-Object Net.Sockets.TcpClient('localhost',8501);$c.Close();break}catch{Start-Sleep -Milliseconds 500}};Start-Process '%ENDERECO%'"
%VP% -m streamlit run dashboard.py --server.headless true --server.port 8501
echo.
echo  O painel foi desligado. Se apareceu "Port 8501 is already in use",
echo  e porque ele ja estava aberto: o navegador mostra o que ja esta rodando.
pause
exit /b

:sem_python
echo.
echo  ERRO: nao achei o Python neste computador.
echo  Instale o Python 3.12 pelo site https://www.python.org/downloads/
echo  marcando a opcao "Add python.exe to PATH", e rode este arquivo de novo.
pause
exit /b 1
