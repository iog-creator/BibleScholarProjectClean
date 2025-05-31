@echo off
set PYTHONPATH=src
python -m web_app > logs\web_app.log 2>&1 