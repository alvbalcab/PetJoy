#!/bin/bash

echo "🚀 Instalando Tienda Online..."
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "Para iniciar el proyecto:"
echo "  1. source venv/bin/activate"
echo "  2. python manage.py runserver"
echo ""
echo "Luego abre: http://127.0.0.1:8000/"
echo "Admin: http://127.0.0.1:8000/admin/"
echo "Usuario: admin@tienda.com"
echo "Contraseña: admin123"
echo ""
