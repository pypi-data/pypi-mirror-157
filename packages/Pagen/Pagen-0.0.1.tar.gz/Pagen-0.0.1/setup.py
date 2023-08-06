from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = ' Generates random password'
LONG_DESCRIPTION = 'This module can create a password of 9 characters'

# Setting up
setup(
    name="Pagen",
    version=VERSION,
    author="Mohammad Mahfuz Rahman",
    author_email="mahfuzrahman038@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['commandtaker', 'wlanpass'],
    keywords=['Password', 'generator', 'bruteforce'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)