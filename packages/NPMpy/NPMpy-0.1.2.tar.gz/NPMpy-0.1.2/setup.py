import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.2'
PACKAGE_NAME = 'NPMpy'
AUTHOR = 'Michael Totty'
AUTHOR_EMAIL = 'MicTott@gmail.com'
URL = 'https://github.com/MicTott/NPMpy'

LICENSE = 'MIT License'
DESCRIPTION = 'Curate Neurophotometrics data for pMat.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'pandas'
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
      packages=find_packages()
      )
