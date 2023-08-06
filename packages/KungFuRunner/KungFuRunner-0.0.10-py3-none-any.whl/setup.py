import os
from setuptools import setup


def readme():
    cwd = os.path.dirname(os.path.abspath(__file__))
    with open(cwd + "/README.md", "r") as file:
        filetext = file.read()
    return filetext


setup(
    name="KungFuRunner",
    version="0.0.10",
    description="A tool for recursively finding and running tests. Like pytest, except you don't have to name your modules with test_",
    # long_description=readme(),
    long_description="",
    long_description_content_type="text/markdown",
    python_requires=">3.5.0",
    url="https://github.com/MadisonAster/KungFu",
    author="Madison Aster",
    author_email="info@MadisonAster.com",
    license="LGPL",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="unit test runner",
    package_data={
        "": ["KungFu.py", "setup.py"],
    },
    packages=[""],
)
