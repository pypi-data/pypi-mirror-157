import os
from setuptools import (setup, find_packages)

with open(
    os.path.join(os.path.dirname(__file__), "requirements/requirement.txt"), "r"
) as fh:
    requirements = fh.readlines()

NAME = "jaki-sdk-python"
DESCRIPTION = (
    "This is a lightweight library that works as a connector to Jaki public API."
)
AUTHOR = "Jaki"
URL = "https://github.com/kobesjava/python-sdk.git"
VERSION = None

about = {}

with open("README.md", "r") as fh:
    about["long_description"] = fh.read()

root = os.path.abspath(os.path.dirname(__file__))

if not VERSION:
    with open(os.path.join(root, "blog", "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

setup(
    name=NAME,
    version=about["__version__"],
    license="MIT",
    description=DESCRIPTION,
    long_description=about["long_description"],
    long_description_content_type="text/markdown",
    author=AUTHOR,
    url=URL,
    keywords=["Jaki", "Public API"],
    install_requires=[req for req in requirements],
    packages=find_packages(),
    python_requires=">=3.6"
)