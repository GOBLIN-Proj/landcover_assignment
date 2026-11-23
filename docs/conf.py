# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LandCover Assignment"
copyright = "2024, Colm Duffy"
author = "Colm Duffy"
release = "0.4.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "html", "index.html", "requirements.txt", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

autoapi_dirs = ["../src/landcover_assignment"]  # location to parse for API reference
nb_execution_mode = "off"  # the example notebook is rendered with its stored outputs, not run
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
# Class docstrings list their attributes and methods; AutoAPI documents them too. Render those sections as fields and
# notes, so each object is described once (otherwise every entry is a "duplicate object description").
napoleon_use_ivar = True
napoleon_custom_sections = [("Methods", "Notes")]
