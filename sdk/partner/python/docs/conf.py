# conf.py - minimal Sphinx configuration for Atom Partner SDK
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Atom Partner SDK'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'alabaster'
master_doc = 'index'