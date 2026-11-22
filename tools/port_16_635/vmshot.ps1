param([int]$Wait = 0, [string]$Serial = '127.0.0.1:16416', [string]$Out = "$env:TEMP\firstlight_vm.png")
# Screenshot helper for the dedicated VM (optional delay, then screencap + focused activity + update size).
$adb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
if ($Wait -gt 0) { Start-Sleep -Seconds $Wait }
& $adb -s $Serial shell "screencap -p /sdcard/s.png" | Out-Null
& $adb -s $Serial pull /sdcard/s.png $Out 2>&1 | Out-Null
& $adb -s $Serial shell "dumpsys activity activities | grep -m1 topResumedActivity; pidof nullsroyale.rel.free; du -sh /data/user/0/nullsroyale.rel.free/update 2>/dev/null; ls /data/user/0/nullsroyale.rel.free/update 2>/dev/null | head -3"
Write-Output "screenshot: $Out"
