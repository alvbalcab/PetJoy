# Testing y Análisis de Calidad - PetJoy

## 📋 Índice
- [Introducción](#introducción)
- [Estructura de Tests](#estructura-de-tests)
- [Instalación de Dependencias](#instalación-de-dependencias)
- [Ejecutar Tests](#ejecutar-tests)
- [Cobertura de Código](#cobertura-de-código)
- [Análisis con SonarQube](#análisis-con-sonarqube)
- [Interpretación de Resultados](#interpretación-de-resultados)

---

## 🎯 Introducción

Este proyecto incluye una suite completa de tests unitarios y de integración, además de configuración para análisis estático de código con SonarQube.

### Tipos de Tests

- **Tests Unitarios**: Verifican el funcionamiento individual de cada componente (modelos, funciones, clases)
- **Tests de Integración**: Verifican la interacción entre diferentes componentes (vistas, formularios, flujos completos)

### Módulos Testeados

- ✅ `productos/` - Modelos y vistas de productos
- ✅ `pedidos/` - Carrito de compras y pedidos
- ✅ `clientes/` - Autenticación y perfiles
- ✅ `core/` - Funcionalidades base

---

## 📁 Estructura de Tests

```
PetJoy-main/
├── productos/
│   ├── tests.py                      # Tests unitarios de modelos
│   └── test_views_integration.py     # Tests de integración de vistas
├── pedidos/
│   ├── tests.py                      # Tests unitarios de modelos
│   └── test_integration.py           # Tests de integración (carrito, checkout)
├── clientes/
│   └── tests.py                      # Tests de autenticación y perfiles
├── core/
│   └── tests.py                      # Tests del módulo core
├── pytest.ini                        # Configuración de pytest
├── .coveragerc                       # Configuración de coverage
├── sonar-project.properties          # Configuración de SonarQube
├── run_tests.sh                      # Script para Linux/Mac
├── run_tests.bat                     # Script para Windows
├── run_sonarqube.sh                  # Script SonarQube Linux/Mac
└── run_sonarqube.bat                 # Script SonarQube Windows
```

---

## 📦 Instalación de Dependencias

### 1. Instalar todas las dependencias

```bash
pip install -r requirements.txt
```

### 2. Dependencias principales de testing

Las siguientes librerías se instalarán:

- `pytest` - Framework de testing
- `pytest-django` - Integración de pytest con Django
- `pytest-cov` - Cobertura de código
- `coverage` - Análisis de cobertura
- `factory-boy` - Generación de datos de prueba
- `faker` - Generación de datos aleatorios

---

## 🧪 Ejecutar Tests

### Opción 1: Scripts Automatizados (Recomendado)

#### En Linux/Mac:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

#### En Windows:
```cmd
run_tests.bat
```

### Opción 2: Comandos Manuales

#### Tests con Django TestCase

```bash
# Todos los tests
python manage.py test

# Tests específicos por módulo
python manage.py test productos
python manage.py test pedidos
python manage.py test clientes
python manage.py test core

# Tests específicos con verbosidad
python manage.py test productos.tests --verbosity=2
```

#### Tests con pytest

```bash
# Todos los tests con cobertura
pytest --cov=productos --cov=pedidos --cov=clientes --cov=core --cov-report=html

# Tests específicos
pytest productos/tests.py
pytest pedidos/test_integration.py

# Con más detalle
pytest -v --tb=short

# Solo tests unitarios (si están marcados)
pytest -m unit

# Solo tests de integración (si están marcados)
pytest -m integration
```

---

## 📊 Cobertura de Código

### Generar Reportes de Cobertura

```bash
# Ejecutar tests con cobertura
coverage run --source='.' manage.py test

# Ver reporte en terminal
coverage report -m

# Generar reporte HTML
coverage html

# Generar reporte XML (para SonarQube)
coverage xml
```

### Ver Reporte HTML

Después de generar el reporte HTML:

```bash
# Linux/Mac
open htmlcov/index.html

# Windows
start htmlcov\index.html
```

### Interpretar la Cobertura

- **Verde (>80%)**: Buena cobertura
- **Amarillo (50-80%)**: Cobertura aceptable, mejorable
- **Rojo (<50%)**: Cobertura insuficiente

**Objetivo**: Mantener cobertura >80% en módulos críticos

---

## 🔍 Análisis con SonarQube

SonarQube analiza la calidad del código, identifica code smells, bugs potenciales, vulnerabilidades de seguridad y duplicación de código.

### Prerequisitos

1. **Instalar SonarQube Server**

   **Opción A: Docker (Recomendado)**
   ```bash
   docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
   ```

   **Opción B: Descarga Manual**
   - Descarga de: https://www.sonarqube.org/downloads/
   - Extrae y ejecuta: `bin/[OS]/sonar.sh start`

2. **Instalar Sonar Scanner**

   **Linux/Mac con Homebrew:**
   ```bash
   brew install sonar-scanner
   ```

   **Manual:**
   - Descarga de: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
   - Añade `bin/` a tu PATH

### Configurar SonarQube

1. **Acceder a SonarQube**
   - URL: http://localhost:9000
   - Usuario: admin
   - Contraseña: admin (cámbiala en el primer acceso)

2. **Crear Token de Autenticación**
   - Ve a: My Account > Security > Generate Token
   - Guarda el token generado

### Ejecutar Análisis

#### Opción 1: Script Automatizado (Recomendado)

**Linux/Mac:**
```bash
# Con token por defecto
./run_sonarqube.sh

# Con token personalizado
SONAR_TOKEN=tu_token_aqui ./run_sonarqube.sh
```

**Windows:**
```cmd
run_sonarqube.bat
```

#### Opción 2: Comando Manual

```bash
sonar-scanner \
  -Dsonar.projectKey=petjoy-tienda-online \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=TU_TOKEN_AQUI
```

### Ver Resultados

Después del análisis, accede a:
- http://localhost:9000/dashboard?id=petjoy-tienda-online

---

## 📈 Interpretación de Resultados

### Métricas de SonarQube

#### 1. **Bugs** 🐛
   - Errores en el código que pueden causar comportamiento incorrecto
   - **Objetivo**: 0 bugs
   - **Prioridad**: Alta

#### 2. **Vulnerabilities** 🔒
   - Problemas de seguridad
   - **Objetivo**: 0 vulnerabilidades
   - **Prioridad**: Crítica

#### 3. **Code Smells** 👃
   - Problemas de mantenibilidad
   - **Objetivo**: Rating A
   - **Prioridad**: Media

#### 4. **Coverage** 📊
   - Porcentaje de código cubierto por tests
   - **Objetivo**: >80%
   - **Prioridad**: Alta

#### 5. **Duplications** 📋
   - Código duplicado
   - **Objetivo**: <3%
   - **Prioridad**: Media

### Ratings de Calidad

- **A**: Excelente (0-5% deuda técnica)
- **B**: Bueno (6-10%)
- **C**: Aceptable (11-20%)
- **D**: Pobre (21-50%)
- **E**: Muy pobre (>50%)

### Quality Gate

Para que el proyecto pase el Quality Gate:

1. ✅ Coverage > 80%
2. ✅ Bugs = 0
3. ✅ Vulnerabilities = 0
4. ✅ Code Smells Rating ≤ A
5. ✅ Duplications < 3%
6. ✅ Security Hotspots reviewed

---

## 🎓 Mejores Prácticas

### Al Escribir Tests

1. **Nomenclatura Clara**
   ```python
   def test_producto_precio_actual_con_oferta(self):
       """Test: Verificar precio actual con oferta"""
   ```

2. **Arrange-Act-Assert**
   ```python
   # Arrange
   producto = Producto.objects.create(...)
   
   # Act
   precio = producto.precio_actual()
   
   # Assert
   self.assertEqual(precio, Decimal("19.99"))
   ```

3. **Tests Independientes**
   - Cada test debe poder ejecutarse solo
   - Usar `setUp()` para configuración común
   - Usar `tearDown()` si es necesario limpiar

4. **Tests Descriptivos**
   - Nombre debe indicar qué se está probando
   - Incluir docstring explicando el propósito

### Mantener Calidad de Código

1. **Ejecutar tests antes de commit**
   ```bash
   ./run_tests.sh
   ```

2. **Revisar cobertura**
   ```bash
   coverage report -m
   ```

3. **Análisis regular con SonarQube**
   ```bash
   ./run_sonarqube.sh
   ```

4. **Corregir issues de SonarQube**
   - Priorizar: Bugs > Vulnerabilities > Code Smells

---

## 🔧 Solución de Problemas

### Tests Fallan

1. **Verificar base de datos de test**
   ```bash
   python manage.py migrate --run-syncdb
   ```

2. **Limpiar archivos compilados**
   ```bash
   find . -name "*.pyc" -delete
   find . -name "__pycache__" -delete
   ```

3. **Verificar dependencias**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

### SonarQube No Conecta

1. **Verificar que el servidor está corriendo**
   ```bash
   curl http://localhost:9000
   ```

2. **Verificar token**
   - Regenerar token en SonarQube
   - Actualizar en comando/script

3. **Verificar configuración**
   - Revisar `sonar-project.properties`
   - Verificar rutas de archivos

### Cobertura Baja

1. **Identificar archivos sin tests**
   ```bash
   coverage report -m --skip-covered
   ```

2. **Añadir tests para código no cubierto**

3. **Excluir código no testeable** (en `.coveragerc`)

---

## 📚 Recursos Adicionales

### Documentación

- [Django Testing](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [Pytest](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [SonarQube](https://docs.sonarqube.org/)

### Tutoriales Recomendados

- [Testing en Django](https://realpython.com/testing-in-django-part-1-best-practices-and-examples/)
- [Pytest para Django](https://pytest-django.readthedocs.io/)
- [SonarQube para Python](https://docs.sonarqube.org/latest/analysis/languages/python/)

---

## 📞 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa esta documentación
2. Consulta los logs de error
3. Busca en la documentación oficial
4. Crea un issue en el repositorio del proyecto

---

## ✅ Checklist de Calidad

Antes de considerar una funcionalidad completa:

- [ ] Tests unitarios escritos y pasando
- [ ] Tests de integración escritos y pasando
- [ ] Cobertura de código >80%
- [ ] SonarQube Quality Gate: PASSED
- [ ] 0 Bugs críticos
- [ ] 0 Vulnerabilidades
- [ ] Documentación actualizada
- [ ] Code review completado

---

**¡Mantener alta calidad de código es responsabilidad de todo el equipo!** 🚀
