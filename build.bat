@echo off
echo ===================================
echo  静かなアラーム時計 -- ビルド開始
echo ===================================

:: PyInstaller がなければインストール
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller をインストール中...
    pip install pyinstaller
)

:: ビルド
pyinstaller --onefile --windowed --name "静かなアラーム時計" clock.py

echo.
echo ビルド完了。dist\ フォルダの「静かなアラーム時計.exe」を使ってください。
pause
