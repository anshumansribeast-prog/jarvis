# Opens AnshuX as a desktop app window (Edge/Chrome app mode — not a normal browser tab).
param(
    [string]$Url = "http://127.0.0.1:8765"
)

$edgePaths = @(
    "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    "$env:LocalAppData\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
)

foreach ($browser in $edgePaths) {
    if (Test-Path $browser) {
        Start-Process -FilePath $browser -ArgumentList @(
            "--app=$Url",
            "--window-size=1280,900",
            "--disable-extensions",
            "--new-window"
        )
        exit 0
    }
}

# Fallback: default handler (may open full browser)
Start-Process $Url
