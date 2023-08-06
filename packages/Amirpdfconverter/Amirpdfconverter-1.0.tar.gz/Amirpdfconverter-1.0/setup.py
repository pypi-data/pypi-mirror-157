import setuptools
from pathlib import Path

from sympy import expand_log


setuptools.setup(
    name="Amirpdfconverter",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["test", "data"])

)
