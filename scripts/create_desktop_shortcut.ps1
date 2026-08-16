# Creates an AnshuX desktop shortcut with the custom icon.
param(
    [switch]$Remove
)

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$launcher = Join-Path $projectRoot "start_ansux.bat"
$iconPath = Join-Path $projectRoot "assets\ansux.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "AnshuX.lnk"

if ($Remove) {
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "Removed AnshuX desktop shortcut."
    } else {
        Write-Host "No AnshuX desktop shortcut found."
    }
    exit 0
}

if (-not (Test-Path $launcher)) {
    Write-Error "start_ansux.bat not found at $launcher"
    exit 1
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 7
$shortcut.Description = "AnshuX — Personal AI Assistant for Anshu"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Save()
Write-Host "AnshuX desktop icon created at:"
Write-Host $shortcutPath
