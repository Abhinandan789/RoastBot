Set objShell = CreateObject("WScript.Shell")
objShell.Run """" & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\start_pet.bat""", 0, False