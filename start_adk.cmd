@echo off
rem Startet die ADK-Weboberflaeche. Python und Umgebung liegen ausserhalb von OneDrive und AppData.
cd /d "%~dp0"
set "UV_PYTHON_INSTALL_DIR=%USERPROFILE%\.uv\python"
set "UV_CACHE_DIR=%USERPROFILE%\.uv\cache"
set "UV_PROJECT_ENVIRONMENT=%USERPROFILE%\.uv\envs\CAS_MyAgents"
set "UV_PYTHON_PREFERENCE=only-managed"
"%USERPROFILE%\.local\bin\uv.exe" run adk web agents --port 8000
