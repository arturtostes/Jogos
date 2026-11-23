@echo off
setlocal
cd /d "%~dp0"
title CHICKEN: THE GAME - Gerador de Executavel

echo ==============================================
echo   CHICKEN: THE GAME - GERAR EXECUTAVEL
 echo ==============================================
echo.

py -3.12 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python 3.12 nao foi encontrado.
    echo Instale o Python 3.12 e marque Add Python to PATH.
    echo.
    pause
    exit /b 1
)

echo [1/3] Instalando/atualizando dependencias de build...
py -3.12 -m pip install --disable-pip-version-check -r requirements.txt pyinstaller
if errorlevel 1 goto :erro

echo.
echo [2/3] Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [3/3] Gerando CHICKEN_THE_GAME.exe...
py -3.12 -m PyInstaller --noconfirm --clean CHICKEN_THE_GAME.spec
if errorlevel 1 goto :erro

echo.
if exist "dist\CHICKEN_THE_GAME.exe" (
    echo ==============================================
    echo   PRONTO!
    echo   dist\CHICKEN_THE_GAME.exe
    echo ==============================================
    explorer "dist"
) else (
    echo [ERRO] O executavel nao apareceu na pasta dist.
)
echo.
pause
exit /b 0

:erro
echo.
echo [ERRO] Falha ao gerar o executavel.
echo Copie a mensagem acima se precisar de ajuda.
echo.
pause
exit /b 1
