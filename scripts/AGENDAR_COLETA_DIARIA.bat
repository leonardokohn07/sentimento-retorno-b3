@echo off
REM ==========================================================================
REM  Cria uma tarefa no Agendador do Windows que roda a coleta da Fase G
REM  todo dia as 19h40 (depois do fechamento da B3). Rode UMA vez.
REM  Para desfazer: REMOVER_AGENDAMENTO.bat
REM ==========================================================================
schtasks /Create /TN "InvestAI coleta diaria" /TR "\"%~dp0coleta_diaria.bat\"" /SC DAILY /ST 19:40 /F
if errorlevel 1 (
    echo.
    echo Nao deu para criar a tarefa. Veja a mensagem acima.
) else (
    echo.
    echo Tarefa criada: "InvestAI coleta diaria", todo dia as 19h40.
    echo O PC precisa estar ligado nesse horario. Log: dados\prospectivo\log_coleta_diaria.txt
)
pause
