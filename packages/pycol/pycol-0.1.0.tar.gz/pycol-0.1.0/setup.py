"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_desc = pathlib.Path(here, "README.md").read_text(encoding="utf-8")

setup(
    name="pycol",
    version="0.1.0",
    description="Simple Python File Packer",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/suzrz/pycol",
    author="suzrz",
    author_email="nemcova.silva@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    keywords="packager, packing, files",
    packages=find_packages(where="."),
    project_urls={
        "Bug Reports": "https://github.com/suzrz/pycol/issues",
        "Source": "https://github.com/suzrz/pycol"
    }
)
