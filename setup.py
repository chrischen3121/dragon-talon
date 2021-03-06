#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
    "scrapy>=2.4.1,<2.5.0",
    "pymongo>=3.11.2,<4.0.0",
    "loguru>=0.5.3,<0.6.0",
]

setup_requirements = [
    "pytest-runner",
]

dev_requirements = [
    "flake8",  # wrapper of pyflakes&pep8
    "pylint",  # code style checking
    "mypy>=0.670",  # type checking
    "isort",  # sorting imports order
    "ipdb",
    "black",  # code formatting
    "wheel",
    "twine",  # upload to pypi
    "black>=20.0",
]

test_requirements = [
    "pytest>=4.0.0,<7.0.0",
]
extras_requirements = {
    "dev": dev_requirements,
    "testing": test_requirements,
    "all": dev_requirements + test_requirements,
}

setup(
    author="chrischen",
    author_email="chrischen3121@gmail.com",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="web crawler for china real estate market",
    entry_points={
        "console_scripts": [
            "dragon_talon=dragon_talon.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="dragon_talon",
    name="dragon_talon",
    packages=find_packages(include=["dragon_talon", "dragon_talon.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    extras_require=extras_requirements,
    url="https://github.com/chrischen3121/dragon_talon",
    version="0.1.2",
    zip_safe=False,
)
