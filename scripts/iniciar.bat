@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo WMK Geo Bridge - API local
py -3 src\bridge.py
pause
