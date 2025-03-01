# Configuration file for the Sphinx documentation builder.
import os
import sys
from unittest.mock import MagicMock  # mock imports
from pygments.styles import get_all_styles

styles = list(get_all_styles())

sys.path.insert(0, os.path.abspath(".."))

html_css_files = [
    'custom.css',
]

# Prevent from unnistalled requierements for nvna
# Please add them in alphabetical order to avoid repetition.
deps = (
    "numpy",
    "pyserial",
)

for package in deps:
    sys.modules[package] = MagicMock()

import nvna

# -- Project information -----------------------------------------------------
project = nvna.__project__
copyright = nvna.__copyright__
author = nvna.__contributors__
release = nvna.__version__
version = release

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_mdinclude",
    "sphinx_rtd_theme",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store",]

# -- Options for HTML output -------------------------------------------------
# Web site
html_title = f"{project} {version}"  # document title
#html_logo = "__logo/logo.png"  # project logo

# Rendering options
myst_heading_anchors = 2  # Generate link anchors for sections.
html_copy_source = False  # Copy documentation source files?
html_show_copyright = False  # Show copyright notice in footer?
html_show_sphinx = False  # Show Sphinx blurb in footer?

# Rendering style
html_theme = "furo"  # custom theme with light and dark mode
pygments_style = "friendly"  # syntax highlight style in light mode
pygments_dark_style = "stata-dark"  # syntax highlight style in dark mode
html_static_path = ["style"]  # folders to include in output
html_css_files = ["custom.css"]  # extra style files to apply

# Sources options
napoleon_include_special_with_doc = True     # Add __init__, __call__, ... methods to the doc if documented
autodoc_member_order = 'bysource' # keep the order of class and function source files
#                                   (thus don't use alphabetical order)
autosummary_generate = True

autosummary_ignore_module_all = False
