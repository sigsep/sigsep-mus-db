# -*- coding: utf-8 -*-

import sys
import os
import shlex
import sphinx_rtd_theme

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'numpydoc'
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = u'dsdeval'
copyright = u'2015, Fabian-Robert Stöter'
author = u'Fabian-Robert Stöter'

version = u'0.1.0'
release = u'0.1.0'

language = None

exclude_patterns = ['_build']

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = "sphinx_rtd_theme"

html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']

htmlhelp_basename = 'dsdevaldoc'

latex_elements = {
}

latex_documents = [
  (master_doc, 'dsdeval.tex', u'dsdeval Documentation',
   u'Fabian-Robert Stöter', 'manual'),
]

man_pages = [
    (master_doc, 'dsdeval', u'dsdeval Documentation',
     [author], 1)
]

texinfo_documents = [
  (master_doc, 'dsdeval', u'dsdeval Documentation',
   author, 'dsdeval', 'One line description of project.',
   'Miscellaneous'),
]
