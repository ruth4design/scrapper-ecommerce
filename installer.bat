@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Nombre del instalador de Python a descargar
SET InstallerName=python-3.9.5-amd64.exe
:: URL de descarga del instalador de Python (Reemplaza esto con la URL actual)
SET PythonURL=https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe

:: Verifica si Python ya está instalado
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo Python ya está instalado.
    GOTO END
)

echo Python no está instalado. Iniciando descarga e instalación.

:: Descarga el instalador de Python usando PowerShell
powershell -Command "Invoke-WebRequest -Uri !PythonURL! -OutFile !InstallerName!"

:: Instala Python
echo Instalando Python...
!InstallerName! /quiet InstallAllUsers=1 PrependPath=1

:: Espera un momento para que la instalación finalice
TIMEOUT /T 5 /NOBREAK >nul

:: Verifica la instalación de Python
python --version
IF %ERRORLEVEL% NEQ 0 (
    echo Hubo un problema con la instalación de Python.
    GOTO END
)

echo Python se instaló correctamente.

:END
ENDLOCAL
