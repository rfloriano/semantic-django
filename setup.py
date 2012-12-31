import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="semantic-django",
    version="0.0.1",
    author="Rafael Floriano da Silva",
    author_email="rflorianobr@gmail.com",
    description=("Make semantic projects using Django and tiplestore databases"),
    license="BSD",
    keywords="semantic django",
    url="http://github.com/rfloriano/semantic-django",
    packages=["semantic"],
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
