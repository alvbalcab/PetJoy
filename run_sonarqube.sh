#!/bin/bash

# Script para ejecutar análisis de SonarQube
# ============================================

echo "==========================================="
echo "  ANÁLISIS SONARQUBE - PROYECTO PETJOY"
echo "==========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encuentra manage.py${NC}"
    echo "Por favor, ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que existe sonar-project.properties
if [ ! -f "sonar-project.properties" ]; then
    echo -e "${RED}Error: No se encuentra sonar-project.properties${NC}"
    echo "Por favor, asegúrate de que el archivo de configuración existe"
    exit 1
fi

echo -e "${BLUE}Prerequisitos:${NC}"
echo "1. SonarQube Server debe estar ejecutándose"
echo "2. Sonar Scanner debe estar instalado"
echo ""
echo "Verifica que SonarQube esté corriendo en:"
echo "  http://localhost:9000 (por defecto)"
echo ""
echo "¿Continuar con el análisis? (s/n)"
read -r response
if [[ ! "$response" =~ ^[Ss]$ ]]; then
    echo "Análisis cancelado"
    exit 0
fi

echo ""
echo -e "${GREEN}Paso 1: Ejecutando tests y generando reportes de cobertura...${NC}"
echo "-------------------------------------------"
./run_tests.sh

echo ""
echo -e "${GREEN}Paso 2: Verificando archivos de reporte...${NC}"
echo "-------------------------------------------"
if [ -f "coverage.xml" ]; then
    echo -e "${GREEN}✓ coverage.xml encontrado${NC}"
else
    echo -e "${YELLOW}⚠ coverage.xml no encontrado${NC}"
    echo "Se continuará sin reporte de cobertura"
fi

echo ""
echo -e "${GREEN}Paso 3: Ejecutando SonarQube Scanner...${NC}"
echo "-------------------------------------------"

# Verificar si sonar-scanner está instalado
if ! command -v sonar-scanner &> /dev/null; then
    echo -e "${RED}Error: sonar-scanner no está instalado${NC}"
    echo ""
    echo "Para instalar SonarQube Scanner:"
    echo "  1. Descarga desde: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
    echo "  2. Extrae el archivo"
    echo "  3. Añade el directorio bin/ a tu PATH"
    echo ""
    echo "Alternativamente, en macOS/Linux con Homebrew:"
    echo "  brew install sonar-scanner"
    exit 1
fi

# Ejecutar sonar-scanner
echo "Ejecutando análisis..."
sonar-scanner \
  -Dsonar.projectKey=petjoy-tienda-online \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=${SONAR_TOKEN:-admin}

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "==========================================="
    echo -e "${GREEN}   ✓ ANÁLISIS COMPLETADO EXITOSAMENTE${NC}"
    echo "==========================================="
    echo ""
    echo "Puedes ver los resultados en:"
    echo -e "${BLUE}http://localhost:9000/dashboard?id=petjoy-tienda-online${NC}"
    echo ""
else
    echo ""
    echo "==========================================="
    echo -e "${RED}   ✗ ERROR EN EL ANÁLISIS${NC}"
    echo "==========================================="
    echo ""
    echo "Posibles causas:"
    echo "  - SonarQube server no está ejecutándose"
    echo "  - Token de autenticación inválido"
    echo "  - Configuración incorrecta en sonar-project.properties"
    echo ""
    exit 1
fi

echo ""
echo -e "${YELLOW}Notas:${NC}"
echo "  - Para usar un token personalizado, ejecuta:"
echo "    SONAR_TOKEN=tu_token ./run_sonarqube.sh"
echo ""
echo "  - Para iniciar SonarQube localmente con Docker:"
echo "    docker run -d --name sonarqube -p 9000:9000 sonarqube:latest"
echo ""
