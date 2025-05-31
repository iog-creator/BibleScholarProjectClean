@echo off
set PYTHONPATH=src
python -m api.contextual_insights_api > logs\contextual_insights_api.log 2>&1 