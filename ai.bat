@echo off
for /f "delims=" %%i in ('python ai.py '''%*''' -shell="cmd"') do set "COMMAND=%%i"
set "user_answer="
set /p user_answer="AI Cmd: [%COMMAND%] execute? (y/n) "
if /i "%user_answer%"=="Y" (
%COMMAND%
)