@echo off
REM Script para ejecutar tests del proyecto PetJoy en Windows
REM ===========================================================

echo ===========================================
echo    EJECUTANDO TESTS - PROYECTO PETJOY
echo ===========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo Error: No se encuentra manage.py
    echo Por favor, ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

echo [1/5] Instalando dependencias de testing...
pip install -q pytest pytest-django pytest-cov coverage factory-boy faker

echo.
echo [2/5] Ejecutando tests unitarios...
echo -------------------------------------------
python manage.py test productos.tests --verbosity=2
python manage.py test pedidos.tests --verbosity=2
python manage.py test clientes.tests --verbosity=2
python manage.py test core.tests --verbosity=2

echo.
echo [3/5] Ejecutando tests de integracion...
echo -------------------------------------------
python manage.py test productos.test_views_integration --verbosity=2
python manage.py test pedidos.test_integration --verbosity=2

echo.
echo [4/5] Ejecutando todos los tests con pytest y coverage...
echo -------------------------------------------
pytest --cov=productos --cov=pedidos --cov=clientes --cov=core --cov-report=html --cov-report=xml --cov-report=term-missing --cov-branch --verbose

echo.
echo [5/5] Generando reporte de cobertura...
echo -------------------------------------------
coverage report -m
coverage html
coverage xml

echo.
echo ===========================================
echo    TESTS COMPLETADOS
echo ===========================================
echo.
echo Reportes generados:
echo   - Reporte HTML: htmlcov\index.html
echo   - Reporte XML: coverage.xml
echo.
echo Para ver el reporte HTML ejecuta: start htmlcov\index.html
echo.
pause
