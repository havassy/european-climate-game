@echo off
echo ==========================================
echo    EUROPEAN CLIMATE GAME - Git Upload
echo ==========================================
echo.

REM Aktuális könyvtár ellenőrzése
echo Jelenlegi könyvtár: %cd%
echo.

REM Git status megjelenítése
echo [1/5] Git status ellenőrzése...
git status
echo.

REM Új/módosított fájlok hozzáadása
echo [2/5] Fájlok hozzáadása a git-hez...
git add .
echo.

REM Commit üzenet bekérése
set /p commit_message="Add meg a commit üzenetet (vagy nyomj Enter a default-hoz): "

REM Default commit üzenet, ha üres
if "%commit_message%"=="" (
    set commit_message=Frissítés: European Climate Game fejlesztés
)

echo.
echo [3/5] Commit létrehozása: "%commit_message%"
git commit -m "%commit_message%"
echo.

REM Push a GitHub-ra
echo [4/5] Feltöltés GitHub-ra...
git push origin main
echo.

REM Eredmény
echo [5/5] Kész!
echo.
echo GitHub Pages URL: https://havassy.github.io/european-climate-game/
echo GitHub Repo URL: https://github.com/havassy/european-climate-game
echo.

REM Opcionális: böngésző megnyitása
set /p open_browser="Megnyissam a GitHub Pages oldalt? (y/n): "
if /i "%open_browser%"=="y" (
    start https://havassy.github.io/european-climate-game/
)

pause