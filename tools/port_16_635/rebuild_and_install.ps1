# Rebuild probe + offline APK and reinstall it on the dedicated VM (port helper).
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
& .\build_offline_engine.ps1 -InputApk .\user-provided\nulls-royale.apk -OutputApk (Join-Path (Get-Location) 'build\cr-ai-offline.apk') *>&1 |
    ForEach-Object { "$_" } | Where-Object { $_ -match '^\[|Built:|error|failed' }
if (-not (Test-Path .\build\cr-ai-offline.apk)) { throw 'build failed' }
& .\install_offline_engine.ps1 -Apk .\build\cr-ai-offline.apk *>&1 | ForEach-Object { "$_" } | Select-Object -Last 4
