#!/usr/bin/env python

from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="flask_appconfigure",
    version="1.0.1",
    description="Flask Application Configurator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tibotix",
    author_email="tizian@seehaus.net",
    url="https://github.com/tibotix/flask_appconfigure",
    package_dir={"flask_appconfigure": "src"},
    packages=["flask_appconfigure"],
    install_requires=["flask"],
    extras_require={"test": ["pytest"]},
    python_requires=">=3.7, <4",
)
