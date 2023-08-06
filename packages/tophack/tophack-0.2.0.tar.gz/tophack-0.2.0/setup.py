#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["beautifulsoup4", "requests"]

test_requirements = []

setup(
    author="Josh Michael Karamuth",
    author_email="michael@confuzeus.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Get top links from HN",
    entry_points={
        "console_scripts": [
            "tophack=top_hack.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="top_hack",
    name="tophack",
    packages=find_packages(include=["top_hack", "top_hack.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/confuzeus/top_hack",
    version="0.2.0",
    zip_safe=False,
)
