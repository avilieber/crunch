from setuptools import setup

NAME = "crunch"
VERSION = "0.0.1"
PACKAGES = ["crunch", "crunch.tests"]
PACKAGE_DATA = {"crunch": ["tests/test_data/*", "tests/test_data/*/*"]}

setup(name=NAME, version=VERSION, packages=PACKAGES, package_data=PACKAGE_DATA)
