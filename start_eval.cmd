@echo off
rem Startet die Evals (automatische Tests) fuer den Kurs_Workflow. Dauert ca. 30 Sekunden.
rem Der Server von start_adk.cmd darf dabei laufen.
cd /d "%~dp0"
set "UV_PYTHON_INSTALL_DIR=%USERPROFILE%\.uv\python"
set "UV_CACHE_DIR=%USERPROFILE%\.uv\cache"
set "UV_PROJECT_ENVIRONMENT=%USERPROFILE%\.uv\envs\CAS_MyAgents"
set "UV_PYTHON_PREFERENCE=only-managed"
rem Damit der Workflow die Tools aus Kurs_Assistent findet:
set "PYTHONPATH=%~dp0agents"
set "PYTHONIOENCODING=utf-8"
rem --group eval: beim ersten Mal laedt uv die Eval-Pakete (ca. 115 MB, 1-2 Minuten)
"%USERPROFILE%\.local\bin\uv.exe" run --group eval adk eval agents\Kurs_Workflow agents\Kurs_Workflow\kurs_workflow.evalset.json --print_detailed_results
pause
