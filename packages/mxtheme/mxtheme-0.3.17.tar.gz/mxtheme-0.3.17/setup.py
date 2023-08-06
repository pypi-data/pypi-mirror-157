from setuptools import setup

with open('mxtheme/_version.py') as ver_file:
    exec(ver_file.read())

setup(
    name = 'mxtheme',
    version = __version__,
    install_requires=['sphinx>=2.2.1'],
    author = 'Mu Li',
    author_email= '',
    url="https://github.com/mli/mx-theme",
    description='A Sphinx theme based on Material Design, adapted from sphinx_materialdesign_theme',
    packages = ['mxtheme'],
    include_package_data=True,
    license= 'MIT License',
    entry_points = {
        'sphinx.html_themes': [
            'mxtheme = mxtheme',
        ]
    },
)
