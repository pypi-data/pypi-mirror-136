from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'Download e analisi dati tramite API Fred '
LONG_DESCRIPTION = 'Package che permette di analizzare, graficare, scaricare e memorizzare dati ottenuti dall\' API Fred.'

# Setting up
setup(
    name="APIFredTorVergata",
    version=VERSION,
    author="Luca Fiscariello",
    author_email="<lucafiscariello@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas', 'datetime', 'numpy','seaborn','matplotlib'],
    keywords=['API', 'Fred', 'Database', 'Download'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
