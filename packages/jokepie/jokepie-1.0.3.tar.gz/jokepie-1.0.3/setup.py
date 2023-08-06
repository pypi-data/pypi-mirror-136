from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '1.0.3'
DESCRIPTION = "API Wrapper for sv443's joke api"
LONG_DESCRIPTION = 'This package allows you to easily get and post jokes to the api formatted using classes!'

# Setting up
setup(
    name="jokepie",
    version=VERSION,
    author="TheWever (Wever#3255)",
    author_email="<nonarrator@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['datetime'],
    keywords=['python', 'jokes', 'api-wrapper', 'api wrapper', 'nv443', 'requests'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
