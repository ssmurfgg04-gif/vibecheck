@echo off
echo ========================================================
echo   Publishing VibeCheck (vibecheck-scan) to npm Registry
echo ========================================================
echo.

cd /d "%~dp0"

echo 1. Checking npm login...
call npm whoami
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] You are not logged into npm.
    echo Please run: npm login
    pause
    exit /b 1
)

echo.
echo 2. Running dry-run check...
call npm publish --dry-run
if %ERRORLEVEL% NEQ 0 (
    echo [!] Dry-run failed. Check package files.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo Dry-run passed! Ready to publish to npm.
echo ========================================================
set /p CONFIRM="Publish publicly to npm now? (y/N): "
if /i "%CONFIRM%"=="y" (
    call npm publish --access public
    echo.
    echo [SUCCESS] Package published! Users can now run:
    echo   npx vibecheck-scan
) else (
    echo Publishing canceled.
)

pause
