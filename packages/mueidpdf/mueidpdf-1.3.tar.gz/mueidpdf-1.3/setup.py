from importlib_metadata import version
import setuptools
from pathlib import Path

setuptools.setup(
    name="mueidpdf",
    version=1.3,
    long_description=Path("README.md").read_text(),
    packages=["mueidpdf"]
)
