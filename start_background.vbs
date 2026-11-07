Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\OPIUM\Downloads\olxparcer"
WshShell.Run "uv run python main.py", 0, False
