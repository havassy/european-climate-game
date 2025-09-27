@echo off
setlocal enabledelayedexpansion
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

REM Create timestamp for backup (fixed Windows format)
for /f "tokens=1-3 delims=. " %%a in ('date /t') do (
    set datestr=%%c-%%b-%%a
)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set timestr=%%a-%%b
)
set timestamp=!datestr!_!timestr: =0!

REM BACKUP SECTION
echo [BACKUP] Creating safety backup before upload...
set backup_dir=backup\!timestamp!
if not exist "backup" mkdir backup
if not exist "!backup_dir!" mkdir "!backup_dir!"

REM Copy important files to backup
if exist "index.html" copy "index.html" "!backup_dir!\" >nul 2>&1
if exist "js" xcopy /E /I /Q "js" "!backup_dir!\js\" >nul 2>&1
if exist "css" xcopy /E /I /Q "css" "!backup_dir!\css\" >nul 2>&1
if exist "README.md" copy "README.md" "!backup_dir!\" >nul 2>&1

echo Backup created: !backup_dir!
echo.

REM Ask if user wants to create a version tag
set /p create_tag="Create version tag before upload? (y/n): "
if /i "!create_tag!"=="y" (
    set /p tag_name="Tag name (e.g., v1.1): "
    set /p tag_message="Tag description: "
    git tag -a "!tag_name!" -m "!tag_message!"
    if !errorlevel! equ 0 (
        echo Tag created: !tag_name!
    ) else (
        echo Error creating tag!
    )
    echo.
)

REM Git status check
echo [1/5] Checking Git status...
git status
echo.

REM Add files (excluding backup directory)
echo [2/5] Adding files to Git...
git add . --ignore-errors
if %errorlevel% neq 0 (
    echo WARNING: Some files could not be added, continuing...
)
echo.

REM Get commit message
set /p commit_message="Enter commit message (or press Enter for default): "

REM Default commit message if empty
if "!commit_message!"=="" (
    set commit_message=Update: automated commit via upload script
)

echo.
echo [3/5] Creating commit: "!commit_message!"
git commit -m "!commit_message!"
if %errorlevel% neq 0 (
    echo No changes to commit or commit failed.
    echo.
)

REM Push to remote (including tags if created)
echo [4/5] Pushing to remote repository...
if /i "!create_tag!"=="y" (
    git push origin !current_branch! --tags
) else (
    git push origin !current_branch!
)
if %errorlevel% neq 0 (
    echo ERROR: Push failed! Check your remote configuration and network connection.
    echo.
    echo Press any key to continue anyway...
    pause >nul
)

REM Success message
echo.
echo [5/5] Done!
echo.

REM Show backup info
echo Backup location: !backup_dir!
echo To restore from backup, copy files from backup folder to project root.
echo.

REM Try to get remote URL for display
for /f "tokens=*" %%i in ('git remote get-url origin 2^>nul') do set remote_url=%%i
if not "!remote_url!"=="" (
    echo Remote repository: !remote_url!
    
    REM Try to extract GitHub Pages URL if it's a GitHub repo
    echo !remote_url! | find "github.com" >nul
    if !errorlevel!==0 (
        set "url_temp=!remote_url!"
        set "url_temp=!url_temp:https://github.com/=!"
        set "url_temp=!url_temp:.git=!"
        for /f "tokens=1,2 delims=/" %%a in ("!url_temp!") do (
            echo Possible GitHub Pages URL: https://%%a.github.io/%%b/
        )
    )
)
echo.

REM Optional: open repository in browser
set /p open_browser="Open remote repository in browser? (y/n): "
if /i "!open_browser!"=="y" (
    if not "!remote_url!"=="" (
        REM Convert SSH URL to HTTPS for browser
        set browser_url=!remote_url!
        set browser_url=!browser_url:git@github.com:=https://github.com/!
        set browser_url=!browser_url:.git=!
        start !browser_url!
    )
)

echo.
echo Upload process completed. Press any key to exit...
pause >nul