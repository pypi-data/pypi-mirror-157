import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.2'
PACKAGE_NAME = 'py7z' 
AUTHOR = 'Jean Diaz' 
AUTHOR_EMAIL = 'jeancodiaz148@gmail.com'
URL = 'https://github.com/drug0drug' 

LICENSE = 'MIT' #Tipo de licencia
DESCRIPTION = 'Librería con funciones ya echas para ahorrarnos trabajo usando py7zr'
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding='utf-8') 
LONG_DESC_TYPE = "text/markdown"


INSTALL_REQUIRES = [
      'py7zr'
      ]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)