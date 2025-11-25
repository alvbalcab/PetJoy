#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modifica esta línea según tu gestor de paquetes (pip, poetry, etc.)
pip install -r requirements.txt

# Convierte archivos estáticos
python manage.py collectstatic --no-input

# Aplica cualquier migración pendiente de base de datos
python manage.py migrate

# Ejecuta el script de personalización
python personalizar_petjoy.py