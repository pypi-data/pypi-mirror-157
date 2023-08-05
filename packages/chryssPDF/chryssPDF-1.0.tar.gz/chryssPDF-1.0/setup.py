#needed for us to be able to publish the module

from ensurepip import version
from pathlib import Path
import setuptools
setuptools.setup(
    name ="chryssPDF",
    version = 1.0,
    long_description = Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
    )