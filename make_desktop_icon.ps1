# Creates Desktop shortcuts for the ANSHUX work area (Windows).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath("Desktop")
$shell = New-Object -ComObject WScript.Shell

$icon = "$env:SystemRoot\System32\imageres.dll,109"
$cursorCandidates = @(
    "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
    "$env:LOCALAPPDATA\Programs\Cursor\Cursor.exe",
    "${env:ProgramFiles}\Cursor\Cursor.exe"
)
foreach ($c in $cursorCandidates) {
    if (Test-Path $c) {
        $icon = "$c,0"
        break
    }
}

function New-AnshxShortcut([string]$fileName, [string]$target) {
    $path = Join-Path $desktop $fileName
    $s = $shell.CreateShortcut($path)
    $s.TargetPath = $target
    $s.WorkingDirectory = $root
    $s.WindowStyle = 1
    $s.Description = "ANSHUX work area — OpenCode, Ada, Jarvis, Semicolon"
    $s.IconLocation = $icon
    $s.Save()
    Write-Host "Created $path"
}

$open = Join-Path $root "open_anshux.bat"
$menu = Join-Path $root "team.bat"
if (-not (Test-Path $open)) { throw "Missing $open" }
if (-not (Test-Path $menu)) { throw "Missing $menu" }

New-AnshxShortcut "ANSHUX.lnk" $open
New-AnshxShortcut "ANSHUX commands.lnk" $menu

Write-Host ""
Write-Host "Double-click ANSHUX on the Desktop to open the work area."
Write-Host "Double-click ANSHUX commands for the number menu (python team.py)."
Write-Host ""
Write-Host "In a terminal always type:  python team.py"
Write-Host "Never:                    python team . py"
