' AnshuX — desktop app launcher (no terminal, no normal browser tabs).
' Double-click this file or the AnshuX icon on your Desktop.

Option Explicit

Dim shell, fso, root, pythonw, http, i, ready, psScript, env

Const HUD_URL = "http://127.0.0.1:8765"

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
Set env = shell.Environment("PROCESS")
root = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = root
psScript = root & "\scripts\open_desktop_app.ps1"

pythonw = root & "\venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonw) Then
  pythonw = "pythonw.exe"
End If

ready = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.Open "GET", HUD_URL & "/api/status", False
http.setTimeouts 2000, 2000, 2000, 2000
http.Send
If Err.Number = 0 And http.Status = 200 Then ready = True
On Error GoTo 0

If Not ready Then
  If Not fso.FileExists(root & "\venv\Scripts\pythonw.exe") Then
    MsgBox "AnshuX is not installed yet." & vbCrLf & vbCrLf & _
           "Double-click INSTALL_ANSHUX.bat in the jarvis folder first.", _
           vbExclamation, "AnshuX"
    WScript.Quit 1
  End If

  env("PYTHONPATH") = root
  env("ANSUX_TEXT_ONLY") = "true"
  env("ANSUX_PUBLIC_URL") = HUD_URL
  env("ANSUX_HUD_HOST") = "127.0.0.1"
  env("ANSUX_OPEN_HUD_ON_START") = "false"

  shell.Run """" & pythonw & """ -m ansux.server", 0, False

  For i = 1 To 60
    WScript.Sleep 500
    On Error Resume Next
    http.Open "GET", HUD_URL & "/api/status", False
    http.setTimeouts 2000, 2000, 2000, 2000
    http.Send
    If Err.Number = 0 And http.Status = 200 Then
      ready = True
      Exit For
    End If
    On Error GoTo 0
  Next
End If

If Not ready Then
  MsgBox "AnshuX could not start." & vbCrLf & vbCrLf & _
         "Run INSTALL_ANSHUX.bat again, or scripts\check_ansux.bat for help.", _
         vbCritical, "AnshuX"
  WScript.Quit 1
End If

shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & psScript & """ -Url """ & HUD_URL & """", 0, False
