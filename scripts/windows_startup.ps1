# Registers AnshuX to start with Windows when enabled in .env
param(
    [switch]$Remove
)

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$batPath = Join-Path $projectRoot "start_ansux.bat"
$startupFolder = [Environment]::GetFolderPath("Startup")
$shortcutPath = Join-Path $startupFolder "AnshuX.lnk"
$iconPath = Join-Path $projectRoot "assets\ansux.ico"

if ($Remove) {
    if (Test-Path $shortcutPath) { Remove-Item $shortcutPath -Force }
    Write-Host "Removed AnshuX from Windows startup."
    exit 0
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $batPath
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 7
$shortcut.Description = "AnshuX Personal AI Assistant"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Save()
Write-Host "AnshuX added to Windows startup."
