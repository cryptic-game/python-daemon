# -- Project information -----------------------------------------------------
import os
import sys


project = "Python Daemon"
copyright = "2020, The Cryptic Python Team"
author = "The Cryptic Python Team"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "sa": ("https://docs.sqlalchemy.org/en/13/", None),
}

# Extend path
sys.path.append(os.path.abspath("../daemon"))

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

add_module_names = False
pygments_style = "friendly"
html_experimental_html5_writer = True
default_role = "code"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "press"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

autodoc_default_options = {
    "members": True,
    "special-members": "__init__",
    "undoc-members": True,
}

autodoc_typehints = "description"

autodoc_member_order = "bysource"

html_copy_source = False
