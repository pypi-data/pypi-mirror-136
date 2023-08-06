import setuptools
from pathlib import Path

setuptools.setup(
    name="mypdfpackage",
    version=2022.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)

# define a Non-duplicate name.
