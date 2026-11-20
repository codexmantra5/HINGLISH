@echo off
title LPU HINGLISH COMPLAINT ROUTER
echo ======================================================================
echo           LPU HINGLISH COMPLAINT ROUTER
echo   "Apni Language Mein Complaint. Right Department Tak Direct."
echo ======================================================================
echo.
echo Starting the AI backend on http://localhost:8000 ...
if not exist "%~dp0.env" (
  echo.
  echo AI_API_KEY is not configured.
  echo Copy .env.example to .env and add your OpenAI API key.
)
cd /d "%~dp0"
start "" http://localhost:8000
python backend\server.py
