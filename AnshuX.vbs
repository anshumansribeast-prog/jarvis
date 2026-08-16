' AnshuX — opens Personal AI in your browser (no terminal window).
' Double-click this file or the desktop AnshuX icon.

Option Explicit

Dim shell, fso, root, pythonw, http, i, ready

Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)

pythonw = root & "\venv\Scripts\pythonw.exe"
If Not fso.FileExists(pythonw) Then
  pythonw = "pythonw.exe"
End If

ready = False
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP.6.0")
http.Open "GET", "http://127.0.0.1:8765/api/status", False
http.Send
If Err.Number = 0 And http.Status = 200 Then ready = True
On Error GoTo 0

If Not ready Then
  Dim cmd
  cmd = "cmd /c cd /d """ & root & """ && " & _
        "set ANSUX_TEXT_ONLY=true&& " & _
        "set ANSUX_PUBLIC_URL=http://127.0.0.1:8765&& " & _
        "set ANSUX_HUD_HOST=127.0.0.1&& " & _
        "set ANSUX_OPEN_HUD_ON_START=false&& " & _
        """" & pythonw & """ -m ansux.server"
  shell.Run cmd, 0, False

  For i = 1 To 40
    WScript.Sleep 500
    On Error Resume Next
    http.Open "GET", "http://127.0.0.1:8765/api/status", False
    http.Send
    If Err.Number = 0 And http.Status = 200 Then
      ready = True
      Exit For
    End If
    On Error GoTo 0
  Next
End If

shell.Run "http://127.0.0.1:8765", 1, False
