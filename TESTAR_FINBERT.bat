@echo off
REM ======================================================================
REM  TESTAR_FINBERT.bat  -  prepara o FinBERT-PT-BR para o painel
REM ======================================================================
REM  1. acha (ou instala) um Python 3.12, que o torch suporta bem no Windows;
REM  2. cria o ambiente separado venv_finbert, so para o FinBERT;
REM  3. instala o torch "CPU" oficial e o transformers nele;
REM  4. testa o modelo e confere com os escores do estudo
REM     (scripts\43_testar_finbert_windows.py);
REM  5. se o torch nao carregar, instala o Visual C++ mais recente e testa de novo.
REM
REM  NAO mexe no venv principal, que e o ambiente da verificacao (99 de 99).
REM  Precisa de internet. Na primeira vez baixa algumas centenas de MB.
REM  O resultado fica em dados\execucao\log_finbert_windows.txt
REM ======================================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set HF_HUB_DISABLE_SYMLINKS_WARNING=1
set VP=venv_finbert\Scripts\python.exe

echo.
echo === FinBERT-PT-BR: preparando o ambiente separado (venv_finbert)
echo.
if exist %VP% goto :instalar

REM ---------------------------------------------------------- 1. Python
set PY=
where py >nul 2>&1
if errorlevel 1 goto :winget_python
echo Pythons instalados neste PC:
py -0
for %%v in (3.12 3.13 3.11) do if not defined PY py -%%v -c "import sys" >nul 2>&1 && set PY=py -%%v
if defined PY goto :criar

echo.
echo Nenhum Python 3.11 a 3.13. Instalando o Python 3.12 pelo gerenciador do Python...
py install 3.12
py -3.12 -c "import sys" >nul 2>&1 && set PY=py -3.12
if defined PY goto :criar
if exist "%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe" set PY="%LOCALAPPDATA%\Python\pythoncore-3.12-64\python.exe"
if defined PY goto :criar

:winget_python
echo.
echo Tentando instalar o Python 3.12 pelo winget (pode pedir permissao)...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PY="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PY py -3.12 -c "import sys" >nul 2>&1 && set PY=py -3.12
if defined PY goto :criar
echo.
echo ERRO: nao consegui um Python 3.12. Instale pelo site python.org (versao 3.12, 64 bits)
echo e rode este arquivo de novo.
goto :fim

:criar
echo.
echo === Criando o venv_finbert com: %PY%
%PY% -m venv venv_finbert
if not exist %VP% (
    echo ERRO: nao consegui criar o venv_finbert.
    goto :fim
)

REM ---------------------------------------------------------- 2. pacotes
:instalar
echo.
echo === Instalando o torch CPU e o transformers (alguns minutos na primeira vez)...
%VP% -m pip install --upgrade pip
%VP% -m pip install torch --index-url https://download.pytorch.org/whl/cpu
%VP% -m pip install transformers huggingface_hub

REM ---------------------------------------------------------- 3. teste
echo.
echo === Testando o FinBERT...
%VP% -u scripts\43_testar_finbert_windows.py
set RES=%errorlevel%
if "%RES%"=="0" goto :ok
if not "%RES%"=="1" goto :fim

REM ---------------------------------------------------------- 4. Visual C++
echo.
echo === O torch nao carregou. Instalando o Visual C++ Redistributable mais recente
echo     (vai pedir permissao de administrador)...
where winget >nul 2>&1
if errorlevel 1 (
    echo Sem winget. Baixe e instale: https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo Depois, reinicie o PC e rode este arquivo de novo.
    goto :fim
)
winget install -e --id Microsoft.VCRedist.2015+.x64 --accept-package-agreements --accept-source-agreements
echo.
echo === Testando de novo...
%VP% -u scripts\43_testar_finbert_windows.py
if "%errorlevel%"=="0" goto :ok
echo.
echo Ainda nao funcionou. Reinicie o PC e rode este arquivo de novo.
echo Se continuar, mande para o Claude o arquivo dados\execucao\log_finbert_windows.txt
goto :fim

:ok
echo.
echo ==================================================================
echo  FINBERT PRONTO. Reinicie o painel (Ctrl+C e streamlit run dashboard.py)
echo  e ligue "Rodar o FinBERT-PT-BR ao vivo" na pagina do sentimento.
echo ==================================================================

:fim
echo.
pause
endlocal
