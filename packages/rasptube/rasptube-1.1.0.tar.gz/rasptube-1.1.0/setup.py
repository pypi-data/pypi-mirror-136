from setuptools import setup

__project__ = "rasptube"
__version__ = "1.1.0"
__description__ = "a python module that automates the process for making videos compatable with the Raspberry Pi"
__packages__ = ["rasptube"]
__author__ = "Walter J Hare"
__keywords__ = ["raspberry pi", "compatability", "youtube"]
__requires__ = ["os"]
__classifiers__ = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Education",
    "Programming Language :: Python :: 3"
]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    classifiers = __classifiers__,
    keywords = __keywords__,
    requires = __requires__
)
