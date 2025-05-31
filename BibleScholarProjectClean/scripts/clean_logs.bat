@echo off
if exist logs\api_server.log del /f /q logs\api_server.log
if exist logs\web_app.log del /f /q logs\web_app.log
if exist logs\contextual_insights_api.log del /f /q logs\contextual_insights_api.log 