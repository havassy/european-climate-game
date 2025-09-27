@echo off
chcp 65001 >nul
echo ==========================================
echo         GIT UPLOAD HELPER SCRIPT
echo ==========================================
echo.

REM Check if we're in a Git repository
if not exist ".git" (
    echo ERROR: This is not a Git repository!
    echo Please navigate to your Git project folder or run 'git init' first.
    pause
    exit /b 1
)

REM Show current directory and branch
echo Current directory: %cd%
for /f "tokens=*" %%i in ('git branch --show-current 2^>nul') do set current_branch=%%i
if "%current_branch%"=="" set current_branch=main
echo Current branch: %current_branch%
echo.

REM Git status check
echo [1/5] Checking Git status...
git status
echo.

REM Add files
echo [2/5] Adding files to Git...
git add .
if %errorlevel% neq 0 (
    echo ERROR: Failed to add files!
    pause
    exit /b 1
)
echo.

REM Get commit message
set /p commit_message="Enter commit message (or press Enter for default): "

REM Default commit message if empty
if "%commit_message%"=="" (
    set commit_message=Update: automated commit via upload script
)

echo.
echo [3/5] Creating commit: "%commit_message%"
git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo No changes to commit or commit failed.
    echo.
)

REM Push to remote
echo [4/5] Pushing to remote repository...
git push origin %current_branch%
if %errorlevel% neq 0 (
    echo ERROR: Push failed! Check your remote configuration and network connection.
    pause
    exit /b 1
)
echo.

REM Success message
echo [5/5] Done!
echo.

REM Try to get remote URL for display
for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set remote_url=%%i
if not "%remote_url%"=="" (
    echo Remote repository: %remote_url%
    
    REM Try to extract GitHub Pages URL if it's a GitHub repo
    echo %remote_url% | find "github.com" >nul
    if %errorlevel%==0 (
        for /f "tokens=4,5 delims=/" %%a in ("%remote_url%") do (
            set username=%%a
            set reponame=%%b
        )
        REM Remove .git extension if present
        setlocal enabledelayedexpansion
        set reponame=!reponame:.git=!
        echo Possible GitHub Pages URL: https://!username!.github.io/!reponame!/
    )
)
echo.

REM Optional: open repository in browser
set /p open_browser="Open remote repository in browser? (y/n): "
if /i "%open_browser%"=="y" (
    if not "%remote_url%"=="" (
        REM Convert SSH URL to HTTPS for browser
        set browser_url=%remote_url%
        set browser_url=!browser_url:git@github.com:=https://github.com/!
        set browser_url=!browser_url:.git=!
        start !browser_url!
    )
)

pause