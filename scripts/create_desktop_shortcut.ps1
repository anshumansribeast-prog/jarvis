# Creates an AnshuX desktop shortcut — opens Personal AI in browser (no terminal).
param(
    [switch]$Remove
)

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$launcher = Join-Path $projectRoot "AnshuX.vbs"
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
    Write-Error "AnshuX.vbs not found at $launcher"
    exit 1
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$launcher`""
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 7
$shortcut.Description = "AnshuX — Personal AI for Anshu (opens in browser)"
if (Test-Path $iconPath) {
    $shortcut.IconLocation = "$iconPath,0"
}
$shortcut.Save()
Write-Host "AnshuX desktop icon created — double-click to open in browser:"
Write-Host $shortcutPath
