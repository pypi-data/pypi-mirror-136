import setuptools
from pathlib import Path

setuptools.setup(
    name="mypdfpkg1",
    version=2022.1,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
