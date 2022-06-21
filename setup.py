from setuptools import setup, find_packages

setup(
    name="malb8dge",
    author="kr8gz",
    url="https://github.com/kr8gz/malb8dge",
    description="malb8dge (thanks bombie) is ANOTHER programming language made by kr8gz who doesn't know how to make programming languages.",

    packages=find_packages(),
    entry_points={"console_scripts": ["malb8dge=malb8dge.malb8dge"]},
)
