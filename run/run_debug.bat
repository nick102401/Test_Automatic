@echo off
set date=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%

pytest %~dp0\..\FastApi\scripts\demo --html=log\report_%date%.html --json=demo.json --alluredir=allure_report --clean-alluredir

allure serve --port 30000 allure_report

Pause

