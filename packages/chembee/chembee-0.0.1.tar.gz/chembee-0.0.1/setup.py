from setuptools import setup

import setuptools

with open("README.md", "r") as fh:

    long_description = fh.read()

setuptools.setup(
    name="chembee",  # Replace with your username
    version="0.0.1",
    author="Julian M. Kleber",
    author_email="juilian.kleber@sail.black",
    description="Package for using Machine Learning and AI for designing chemicals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.codeberg/cap_jmk/chembee",
    packages=setuptools.find_packages(include=["chembee*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: APGL 3.0 License or later",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
