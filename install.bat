@echo off
echo 🚀 Instalando Tienda Online...
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado. Por favor instálalo primero.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo.
echo ✅ ¡Instalación completada!
echo.
echo Para iniciar el proyecto:
echo   1. venv\Scripts\activate
echo   2. python manage.py runserver
echo.
echo Luego abre: http://127.0.0.1:8000/
echo Admin: http://127.0.0.1:8000/admin/
echo Usuario: admin@tienda.com
echo Contraseña: admin123
echo.
pause
