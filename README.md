# INSTRUCCIONES DE INSTALACIÓN Y PUESTA EN PRODUCCIÓN

## 1.🚀 Configuración del Entorno (Requisitos Previos)
Esta sección informa qué necesita el usuario antes de empezar.
- Tener Python 3.12 instalado. **https://www.python.org/downloads/**
- Sistema de Control de Versiones como Git.



## 2.⚙️ Instalación y Preparación del Proyecto
| Título | Descripción | Comandos |
|---|---|---|
| **Instalar Visual Studio Code (VSC)** | Instalar entorno de desarrollo | **https://code.visualstudio.com/** |
| **Clonar el Repositorio** | Clonar repositorio desde GitHub | `git clone https://github.com/alvbalcab/PetJoy.git` |
| **Navegar al Directorio** | Entrar a la carpeta principal del proyecto. | `cd PetJoy` |
| **Crear Entorno Virtual** | Crear entorno virtual Python | `python -m venv .venv` |
| **Activar Entorno Virtual** | Poner el entorno en uso | **Windows:** `.\.venv\Scripts\activate.bat`<br>**Linux/macOS:** `source .venv/bin/activate` |
| **Instalar Django** | Instalar Django | `python -m pip install Django` |
| **Instalar Dependencias** | Instalar librerías necesarias: `requirements.txt`  | `python -m pip install -r requirements.txt` |


## 3.💾 Configuración de la Base de Datos
Esta sección prepara la base de datos para su uso inicial:
* Crear tablas de la base de datos: `python manage.py migrate`
* Cargar datos iniciales (solo es necesario ejecutarlo una vez para cargar todos los productos): `python personalizar_petjoy.py `


## 4.▶️ Ejecutar la aplicación (Puesta en Desarrollo)
Instrucciones para  que el usuario pueda ver el proyecto funcionando localmente.
* Ejecutar el Servidor de Desarrollo (dentro del entorno virtual de python **.venv**): `python manage.py runserver`
* Ejecutar el Servidor de Desarrollo (dentro del entorno virtual de python **.venv**): `python personalizar_petjoy.py`
* Acceso: URL por defecto **(http://127.0.0.1:8000/)**


## 5.🛠️ Comandos comunes de desarrollo
| Acción | Descripción | Comando |
|---|---|---|
| **Crear Superusuario** | Para acceder al panel de administración de Django | `python manage.py createsuperuser` |
| **Crear migraciones** | Si se hacen cambios en models.py | `python manage.py makemigrations` |
| **Aplicar migraciones** | Para actualizar la estructura de la DB | `python manage.py migrate` |


## 6.🌐 Despliegue en Render
Enlace para desplegar el proyecto en Render: **https://petjoy-app.onrender.com**
