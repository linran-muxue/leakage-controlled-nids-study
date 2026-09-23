@echo off
rem Durable launcher for the full-corpus RCCF batch.
rem
rem Started by the scheduled task "CodexRCCF" so the run lives outside the
rem Codex sandbox job: every Codex restart used to kill the supervisor and all
rem three workers.  The supervisor itself holds a named mutex and exits at once
rem if another instance is already running, so a repeating trigger is safe.
setlocal
cd /d "C:\Users\27677\Documents\ChatGPT\论文"
set PY=E:\论文\.venv\Scripts\python.exe

rem Run the batch.  The supervisor starts the anti-standby helper itself when
rem its heartbeat is stale, and exits immediately when the mutex is already
rem held, so a repeating trigger is a cheap liveness check.
"%PY%" -u scripts\run_full_corpus_parallel_v1.py --workers 3 >> logs\supervisor.log 2>> logs\supervisor.err
endlocal
