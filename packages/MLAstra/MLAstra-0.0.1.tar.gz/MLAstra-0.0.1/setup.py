from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Machine Learning and Deep Learning Models'
LONG_DESCRIPTION = 'Implematation of basic Machine Learning and Deep Learning Models from scratch'

# Setting up
setup(
    name="MLAstra",
    version=VERSION,
    author="Shashikant",
    author_email="<shashikantprasad1111@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)