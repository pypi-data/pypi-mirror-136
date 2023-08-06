from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Tool for plotting XRD from the CRYSTAL software'

# Setting up
setup(
    name="pyxrdspec",
    version=VERSION,
    author="Alessandro Cossard",
    author_email="<alessandro.cossard@unito.it>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'quantum', 'xrd', 'chemistry', 'physics', 'spectrum'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
