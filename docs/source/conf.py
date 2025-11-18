# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Text Loom'
copyright = '2025, Text Loom'
author = 'Text Loom'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
import os
import sys
sys.path.insert(0, os.path.abspath('../../../src'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]
napoleon_google_docstring = True

autodoc_default_options = {
    'members': True,          # Document all public members (methods, attributes)
    'undoc-members': False,   # Do not document members without docstrings
    'private-members': False, # Do not document private members (starting with _)
    'special-members': False, # Do not document special members (starting with __)
    'inherited-members': False # <--- **THE KEY SETTING**
}

templates_path = ['_templates']
exclude_patterns = []

language = 'en'
source_encoding = 'utf-8'

# Set permalink icon to suppress warning (default changed in Sphinx 7.2+)
html_permalinks_icon = '¶'

# Disable jQuery SRI to suppress warning (default changed in Sphinx 7.2+)
jquery_use_sri = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
