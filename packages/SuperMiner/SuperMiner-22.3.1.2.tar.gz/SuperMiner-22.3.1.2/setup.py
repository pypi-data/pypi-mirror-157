# _*_ coding:gbk _*_
"""
SuperMiner project setup

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib
import os

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")
setup(
    name="SuperMiner",
    version="22.3.1.2",
    description="Web miner built based on selenium but more simple operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://airscker.github.io/SuperWebMiner/", 
    author="Airscker",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # "License :: OSI Approved :: Mozilla Public License Version 2.0",        
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="web, miner, highly composed",
    packages=find_packages(),
    python_requires=">=3.5, <=3.10",
    install_requires=["requests","urllib3","selenium","lxml","bs4","click","setuptools"],
    entry_points={
        "console_scripts": [
            "Superminer=Superminer:main",
        ],
    },
    project_urls={
        "Project":"https://github.com/Airscker/SuperWebMiner",
    },
)
