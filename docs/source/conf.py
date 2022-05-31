# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'VRKitchen2.0-Tutorial'
copyright = '2022, UCLA'
author = 'Yizhou Zhao, Wensi Ai'

# The short X.Y version.
version = "0.4"
# The full version, including alpha/beta/rc tags.
release = "0.0.4"

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
    'sphinxcontrib.bibtex',
    'nbsphinx',
    'sphinx_rtd_theme',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = "../image/logo.png"

# html_theme_options = {
#     'logo_only': True
# }

html_theme_options = {
    'analytics_id': 'G-XXXXXXXXXX',  #  Provided by Google in your dashboard
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#fccf03',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_static_path = []

html_css_files = ["theme.css"]

# -- Options for EPUB output
epub_show_urls = 'footnote'

# import os
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'genmotion')))

# autodoc_mock_imports = ["bpy", "numpy", "torch", "matplotlib", "IPython", "pickle", "genmotion"]