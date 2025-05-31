@echo off
set PYTHONPATH=src
python -m api.api_app > logs\api_server.log 2>&1 