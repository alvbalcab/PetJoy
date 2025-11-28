# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# --- CONFIGURACIÓN DE ENTORNO DJANGO ------------------------

import os
import sys
import django


sys.path.insert(0, os.path.abspath('..'))

sys.path.insert(0, os.path.abspath('../..'))

sys.path.insert(0, os.path.abspath('../tienda_online'))

# Configura Django para que Sphinx pueda importar módulos (modelos, vistas, etc.).
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tienda_online.settings')
django.setup()

# ----------------------------------------------------------------------------


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PetJoy'
copyright = '2025, G3.12'
author = 'G3.12'
version = '1.0'
release = '1.0'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',    
    'sphinx.ext.todo',        
    'sphinx_rtd_theme',       
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store'] 

language = 'es'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

html_title = "Documentación de PetJoy API y Web"