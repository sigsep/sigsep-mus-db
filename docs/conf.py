# -*- coding: utf-8 -*-

import os

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
else:
    html_theme = 'default'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'numpydoc'
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'dsd100'
copyright = u'2016, Fabian-Robert Stöter'
author = u'Fabian-Robert Stöter'

version = u'0.3.0'
release = u'0.3.0'

language = None

exclude_patterns = ['_build']

pygments_style = 'sphinx'

todo_include_todos = False

html_static_path = ['_static']

htmlhelp_basename = 'dsd100doc'

latex_elements = {
}

latex_documents = [
  (master_doc, 'dsd100.tex', u'dsd100 Documentation',
   u'Fabian-Robert Stöter', 'manual'),
]

man_pages = [
    (master_doc, 'dsd100', u'dsd100 Documentation',
     [author], 1)
]

texinfo_documents = [
  (master_doc, 'dsd100', u'dsd100 Documentation',
   author, 'dsd100', 'One line description of project.',
   'Miscellaneous'),
]
