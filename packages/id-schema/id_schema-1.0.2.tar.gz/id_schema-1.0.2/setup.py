#!/usr/bin/env python

from setuptools import setup
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="id_schema",
    version="1.0.2",
    description="ID Schema",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tibotix",
    author_email="tizian@seehaus.net",
    url="https://github.com/tibotix/id_schema",
    package_dir={"id_schema": "src"},
    packages=["id_schema", "id_schema.components"],
    install_requires=[],
    extras_require={"test": ["pytest"]},
    python_requires=">=3.8, <4",
)
