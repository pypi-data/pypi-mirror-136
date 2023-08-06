import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
VERSION = '1.0.2'
PACKAGE_NAME = 'troop'
AUTHOR = 'kieran gordon'
AUTHOR_EMAIL = 'koo.m.gordon@outlook.com'
URL = 'https://github.com/koogordo/troop'
LICENSE = 'MIT'
DESCRIPTION = ''
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"
INSTALL_REQUIRES = [
      'networkx==2.6.3'
]
setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      py_modules=['troop']
      )