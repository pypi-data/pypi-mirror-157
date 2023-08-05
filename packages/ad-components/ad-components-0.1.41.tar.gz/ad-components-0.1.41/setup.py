#!/usr/bin/env python
from pathlib import Path
from setuptools import setup

version_info = {}
with open("ad/version.py") as fp:
    exec(fp.read(), version_info)

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
    name="ad-components",
    version=version_info["__version__"],
    packages=["ad"],
    install_requires=["dapr~=1.6.1"],
    entry_points={
        "console_scripts": [
            "adc = ad.main:main",
        ],
    },
    author="Accelerated Discovery",
    author_email="jazzar@ibm.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development",
    ],
    url="https://github.ibm.com/Accelerated-Discovery/Discovery-Platform",
    description="Accelerated Discovery Reusable Components.",
    long_description=long_description,
    long_description_content_type="text/markdown",
)
