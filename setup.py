from setuptools import find_packages, setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(
    name="aletheia",
    version="0.1.0",
    description="Projet Aletheia",
    packages=find_packages(),
    install_requires=requirements,
)
