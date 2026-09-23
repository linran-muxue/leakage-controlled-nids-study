' Run the durable full-corpus launcher with no visible console window.
' The scheduled task "CodexRCCF" invokes this file every 30 minutes; the
' supervisor inside exits immediately when it already holds its mutex, so the
' repetition is a cheap liveness check rather than duplicated work.
Dim shell, script
Set shell = CreateObject("WScript.Shell")
script = "C:\Users\27677\Documents\ChatGPT\论文\scripts\start_full_corpus.bat"
shell.Run """" & script & """", 0, False
