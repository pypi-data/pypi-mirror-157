import os
import re
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

PACKAGE_NAME = "osmRoad-nadfity"
AUTHOR = "Muhammad Yasirroni"
AUTHOR_EMAIL = "muhammadyasirroni@gmail.com"
URL = "https://github.com/nadfity/osmRoad"

HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'osm', '__init__.py'), "rt") as f:
    version_line = f.read()
m = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_line, re.M)
__version__ = m.group(1)

setuptools.setup(
    name=PACKAGE_NAME,
    version=__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description="Parse OSM Data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
