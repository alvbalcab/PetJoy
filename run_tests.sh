#!/bin/bash

# Script para ejecutar tests del proyecto PetJoy
# ================================================

echo "==========================================="
echo "   EJECUTANDO TESTS - PROYECTO PETJOY"
echo "==========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encuentra manage.py${NC}"
    echo "Por favor, ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Verificar que existe el entorno virtual
if [ ! -d "venv" ] && [ ! -d "env" ]; then
    echo -e "${YELLOW}Advertencia: No se encontró un entorno virtual${NC}"
    echo "Se recomienda crear uno con: python -m venv venv"
    echo "¿Continuar de todas formas? (s/n)"
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        exit 0
    fi
fi

echo -e "${GREEN}1. Instalando dependencias de testing...${NC}"
pip install -q pytest pytest-django pytest-cov coverage factory-boy faker

echo ""
echo -e "${GREEN}2. Ejecutando tests unitarios...${NC}"
echo "-------------------------------------------"
python manage.py test productos.tests --verbosity=2
python manage.py test pedidos.tests --verbosity=2
python manage.py test clientes.tests --verbosity=2
python manage.py test core.tests --verbosity=2

echo ""
echo -e "${GREEN}3. Ejecutando tests de integración...${NC}"
echo "-------------------------------------------"
python manage.py test productos.test_views_integration --verbosity=2
python manage.py test pedidos.test_integration --verbosity=2

echo ""
echo -e "${GREEN}4. Ejecutando todos los tests con pytest y coverage...${NC}"
echo "-------------------------------------------"
pytest --cov=productos --cov=pedidos --cov=clientes --cov=core \
       --cov-report=html --cov-report=xml --cov-report=term-missing \
       --cov-branch --verbose

echo ""
echo -e "${GREEN}5. Generando reporte de cobertura...${NC}"
echo "-------------------------------------------"
coverage report -m
coverage html
coverage xml

echo ""
echo "==========================================="
echo -e "${GREEN}   ✓ TESTS COMPLETADOS${NC}"
echo "==========================================="
echo ""
echo "Reportes generados:"
echo "  - Reporte HTML: htmlcov/index.html"
echo "  - Reporte XML: coverage.xml"
echo ""
echo -e "Para ver el reporte HTML ejecuta: ${YELLOW}open htmlcov/index.html${NC}"
echo ""
