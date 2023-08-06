import setuptools
from pathlib import Path

setuptools.setup(
    name="Ivan_Analrashpdf",
    version=12.2,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude = ['tests', 'data'])

)