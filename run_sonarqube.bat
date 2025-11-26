@echo off
REM Script para ejecutar analisis de SonarQube en Windows
REM ======================================================

echo ===========================================
echo   ANALISIS SONARQUBE - PROYECTO PETJOY
echo ===========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo Error: No se encuentra manage.py
    echo Por favor, ejecuta este script desde el directorio raiz del proyecto
    pause
    exit /b 1
)

REM Verificar que existe sonar-project.properties
if not exist "sonar-project.properties" (
    echo Error: No se encuentra sonar-project.properties
    echo Por favor, asegurate de que el archivo de configuracion existe
    pause
    exit /b 1
)

echo Prerequisitos:
echo 1. SonarQube Server debe estar ejecutandose
echo 2. Sonar Scanner debe estar instalado
echo.
echo Verifica que SonarQube este corriendo en:
echo   http://localhost:9000 (por defecto)
echo.
set /p continue="Continuar con el analisis? (s/n): "
if /i not "%continue%"=="s" (
    echo Analisis cancelado
    pause
    exit /b 0
)

echo.
echo Paso 1: Ejecutando tests y generando reportes de cobertura...
echo -------------------------------------------
call run_tests.bat

echo.
echo Paso 2: Verificando archivos de reporte...
echo -------------------------------------------
if exist "coverage.xml" (
    echo [OK] coverage.xml encontrado
) else (
    echo [ADVERTENCIA] coverage.xml no encontrado
    echo Se continuara sin reporte de cobertura
)

echo.
echo Paso 3: Ejecutando SonarQube Scanner...
echo -------------------------------------------

REM Verificar si sonar-scanner esta instalado
where sonar-scanner >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: sonar-scanner no esta instalado
    echo.
    echo Para instalar SonarQube Scanner:
    echo   1. Descarga desde: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
    echo   2. Extrae el archivo
    echo   3. Aniade el directorio bin\ a tu PATH
    echo.
    pause
    exit /b 1
)

REM Ejecutar sonar-scanner
echo Ejecutando analisis...
sonar-scanner ^
  -Dsonar.projectKey=petjoy-tienda-online ^
  -Dsonar.sources=. ^
  -Dsonar.host.url=http://localhost:9000 ^
  -Dsonar.token=admin

REM Verificar el resultado
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===========================================
    echo    ANALISIS COMPLETADO EXITOSAMENTE
    echo ===========================================
    echo.
    echo Puedes ver los resultados en:
    echo http://localhost:9000/dashboard?id=petjoy-tienda-online
    echo.
) else (
    echo.
    echo ===========================================
    echo    ERROR EN EL ANALISIS
    echo ===========================================
    echo.
    echo Posibles causas:
    echo   - SonarQube server no esta ejecutandose
    echo   - Token de autenticacion invalido
    echo   - Configuracion incorrecta en sonar-project.properties
    echo.
)

echo.
echo Notas:
echo   - Para iniciar SonarQube localmente con Docker:
echo     docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
echo.
pause
