from os import path
from ._version import __version__
from .card import CardDirective


package_dir = path.dirname(path.abspath(__file__))

def get_path():
    return package_dir

def setup(app):
    app.add_html_theme('mxtheme', package_dir)
    return {'version': __version__, 'parallel_read_safe': True}
