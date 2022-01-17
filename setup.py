#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Django>=3.2", "django-fsm>=2.8.0,<3.0"]

test_requirements = []

setup(
    author="Josh Michael Karamuth",
    author_email="michael@confuzeus.com",
    python_requires=">=3.8",
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
    description="Invite people to login or register.",
    install_requires=requirements,
    license="MIT",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="django-getin",
    name="django-getin",
    packages=find_packages(include=["getin", "getin.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/confuzeus/django-getin",
    version="0.1.0",
    zip_safe=False,
)
