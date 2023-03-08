"""Package setup"""

from setuptools import find_packages, setup

setup(
    packages=find_packages(
        include=["x12"],
        exclude=["tests"],
    ),
)
