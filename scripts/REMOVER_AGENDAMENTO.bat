@echo off
REM Remove a tarefa "InvestAI coleta diaria" do Agendador do Windows.
schtasks /Delete /TN "InvestAI coleta diaria" /F
pause
