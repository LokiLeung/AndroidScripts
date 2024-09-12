@REM ====================
@REM TODO
@REM ====================
@REM 1. test the screen record
@REM 2. add the audio record
@REM 3. add quick open apps key

@echo off
color 04
echo.
echo [1m[33mMenu[0m
echo.
echo [1m[33m1. Screenshot[0m
echo [1m[33m2. Record[0m
echo [1m[33m3. Exit[0m

:loop
choice /C 123 /N /M "Choose: "
if errorlevel 3 goto exit
if errorlevel 2 goto record
if errorlevel 1 goto screenshot

:screenshot
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /format:list') do set "timestamp=%%a"
set "screenshotFolder=screenshots"
if not exist "%screenshotFolder%" mkdir "%screenshotFolder%"
set "formattedTimestamp=%timestamp:~0,4%%timestamp:~4,2%%timestamp:~6,2%_%timestamp:~8,2%%timestamp:~10,2%%timestamp:~12,2%"
adb exec-out screencap -p > "%screenshotFolder%\Screenshot_%formattedTimestamp%.png"
echo Screenshot saved as %screenshotFolder%\Screenshot_%formattedTimestamp%.png in current directory.
goto loop

:record
set /p duration="Input record duration (seconds, default is 15): "
if not defined duration set duration=15
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /format:list') do set "timestamp=%%a"
set "recordFolder=records"
if not exist "%recordFolder%" mkdir "%recordFolder%"
adb shell screenrecord --time-limit %duration% /sdcard/Record_%timestamp%_%duration%s.mp4
adb pull /sdcard/Record_%timestamp%_%duration%s.mp4 "%recordFolder%"
echo Record saved as %recordFolder%\Record_%timestamp%_%duration%s.mp4 in current directory.
goto loop

:exit
echo Exit script.
exit /b