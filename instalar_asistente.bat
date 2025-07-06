@echo off
title Instalador de CatMini 🐾
echo ===========================================
echo        CatMini - Instalación Automática
echo ===========================================
echo.

:: Ir al directorio del script
cd /d "%~dp0"

:: Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en el PATH.
    pause
    exit /b
)

:: Crear entorno virtual (si no existe)
if exist .venv (
    echo 🟡 El entorno virtual ya existe. Usando el existente...
) else (
    echo [1/6] Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ❌ Error al crear el entorno virtual.
        pause
        exit /b
    )
    echo ✅ Entorno virtual creado.
)

:: Activar entorno virtual
echo [2/6] Activando entorno virtual...
call .venv\Scripts\activate
if errorlevel 1 (
    echo ❌ Error al activar el entorno virtual.
    pause
    exit /b
)
echo ✅ Entorno virtual activado.

:: Instalar dependencias
echo [3/6] Instalando dependencias...
pip install --upgrade pip
pip install google-generativeai speechrecognition pyttsx3 pyaudio pillow python-dotenv pyinstaller
if errorlevel 1 (
    echo ❌ Error al instalar las dependencias.
    pause
    exit /b
)
echo ✅ Dependencias instaladas correctamente.

:: Verificar archivos requeridos
echo [4/6] Verificando archivos requeridos...
set MISSING=0

if not exist assets\avatar.gif (
    echo ❌ Faltante: assets\avatar.gif
    set MISSING=1
)
if not exist assets\icono.ico (
    echo ❌ Faltante: assets\icono.ico
    set MISSING=1
)
if not exist assets\altavoz.png (
    echo ❌ Faltante: assets\altavoz.png
    set MISSING=1
)
if not exist assets\pause.png (
    echo ❌ Faltante: assets\pause.png
    set MISSING=1
)
if not exist .env (
    echo ❌ Faltante: archivo .env con tu GEMINI_API_KEY
    set MISSING=1
)

if %MISSING%==1 (
    echo 🔴 Por favor, agregá los archivos faltantes y volvé a ejecutar.
    pause
    exit /b
)
echo ✅ Archivos requeridos verificados.

:: Compilar ejecutable
echo [5/6] Compilando CatMini.exe...
pyinstaller --noconsole --onefile --name CatMini --icon=assets/icono.ico --add-data "assets;assets" --add-data ".env;." --distpath ejecutable main.py
if errorlevel 1 (
    echo ❌ Error al compilar el ejecutable.
    pause
    exit /b
)
echo ✅ Ejecutable generado en la carpeta /ejecutable

:: Limpiar archivos temporales
echo [6/6] Limpiando archivos temporales...
rmdir /s /q build >nul 2>&1
rmdir /s /q __pycache__ >nul 2>&1
del main.spec >nul 2>&1

echo.
echo 🐾 CatMini está listo para usarse.
echo 📂 Ejecutable disponible en: ejecutable\CatMini.exe
pause
