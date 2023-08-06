import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.7'
PACKAGE_NAME = 'Fedtools'
AUTHOR = 'David Woroniuk'
AUTHOR_EMAIL = 'david.woroniuk@durham.ac.uk'


LICENSE = 'MIT'
DESCRIPTION = 'An open source library for the extraction of Federal Reserve Data.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'numpy',
    'pandas',
    'requests',
    'beautifulsoup4',
    'fake-useragent',
    'python-dateutil',
    'pytz',
    'six',
    'soupsieve'
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )
