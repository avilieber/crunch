import os.path

from setuptools import setup

NAME = "crunch"
PACKAGES = ["crunch", "crunch.tests"]
PACKAGE_DATA = {"crunch": ["tests/test_data/*", "tests/test_data/*/*"]}

with open(os.path.join("crunch", "_version.py"), "r") as f:
    exec(f.read())
VERSION = __version__  # noqa: F821


def _read_requirements(file):
    return [
        line for line in file.read().split() if len(line) and not line.startswith("#")
    ]


with open("requirements.txt", "r") as f:
    INSTALL_REQUIRES = _read_requirements(f)

with open("requirements-dev.txt") as f:
    EXTRAS_REQUIRE = {"dev": _read_requirements(f), "test": "pytest"}

setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    build_exe_options = {'packages': ['_sysconfigdata_m_darwin_darwin']}
)
