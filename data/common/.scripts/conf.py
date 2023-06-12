"""Template `conf.py` for running `preview.py` on a given document."""

html_title = ""
home_page_in_toc = False
master_doc = "index"
language = "en"
extensions = ["myst_parser", "sphinx_design"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_book_theme"

# Remove the primary sidebar
# https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html#remove-the-primary-sidebar-from-pages
html_sidebars = {"**": []}
