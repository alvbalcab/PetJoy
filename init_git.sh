#!/bin/bash

echo "🚀 Configurando Git para PetJoy..."
echo ""

# Inicializar repositorio
echo "📦 Inicializando repositorio Git..."
git init

# Crear .gitignore
echo "📝 Creando .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Entorno virtual
venv/
env/
ENV/

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Sistema
.DS_Store
Thumbs.db

# Secretos (NO subir a producción)
# settings_local.py
# .env

# Otros
*.bak
*.tmp
EOF

# Agregar todos los archivos
echo "➕ Agregando archivos al staging..."
git add .

# Primer commit
echo "💾 Creando primer commit..."
git commit -m "🐾 Initial commit - PetJoy: Tienda de juguetes para mascotas

- Sistema de e-commerce completo en Django
- Catálogo de productos con filtros
- Carrito de compra funcional
- Sistema de pedidos
- Panel de administración
- 10 productos de ejemplo
- 5 categorías específicas de mascotas
- Diseño responsive con Bootstrap 5"

echo ""
echo "✅ ¡Repositorio Git configurado!"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1️⃣  Crear repositorio en GitHub:"
echo "   - Ve a: https://github.com/new"
echo "   - Nombre: petjoy"
echo "   - Descripción: Tienda online de juguetes para mascotas"
echo "   - Público o Privado (tu elección)"
echo "   - NO inicialices con README, .gitignore ni licencia"
echo ""
echo "2️⃣  Conectar con GitHub:"
echo "   git remote add origin https://github.com/TU_USUARIO/petjoy.git"
echo ""
echo "3️⃣  Subir código:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "💡 Tip: Reemplaza TU_USUARIO con tu nombre de usuario de GitHub"
echo ""
