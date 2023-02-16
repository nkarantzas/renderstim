#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name="renderstim",
    version="0.0",
    description="Rendering stimuli for deep learning",
    author="nkarantzas",
    # author_email="nickoskarantzas@gmail.com",
    packages=find_packages(exclude=[]),
    install_requires=[
        "deeplake",
    ],
)
