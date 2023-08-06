from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

__project__ = "rasptube"
__version__ = "2.0.1"
__description__ = "a python module that automates the process for making videos compatable with the Raspberry Pi"
__packages__ = ["rasptube"]
__author__ = "Walter J Hare"
__keywords__ = ["raspberry pi", "compatability", "youtube"]
__requires__ = ["os"]
__license__ = "MIT"
__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License"
]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = __packages__,
    author = __author__,
    classifiers = __classifiers__,
    keywords = __keywords__,
    requires = __requires__,
    license = __license__
)
