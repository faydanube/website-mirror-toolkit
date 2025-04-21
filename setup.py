#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="website-converter",
    version="1.0.0",
    author="Author",
    author_email="author@example.com",
    description="一站式网站下载、转换工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/website-converter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "markdown>=3.3.0",
        "pathlib>=1.0.0",
        "requests>=2.25.0",
        "beautifulsoup4>=4.9.0",
        "flask>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "website-converter=website_converter.cli:main",
        ],
    },
)
