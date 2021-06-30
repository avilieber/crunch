from setuptools import setup


NAME="luc"
VERSION="0.0.1"
PACKAGES = ['luc', 'luc.tests']
PACKAGE_DATA = {
    'luc': [
        'tests/test_data/*',
        'tests/test_data/*/*'
    ]
}

setup(
    name=NAME,
    version=VERSION,
    packages=PACKAGES,
    package_data=PACKAGE_DATA
)