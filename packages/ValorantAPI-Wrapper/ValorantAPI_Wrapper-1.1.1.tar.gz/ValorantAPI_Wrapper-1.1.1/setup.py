from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_desc = fh.read()

setup(
    name="ValorantAPI_Wrapper",
    version="1.1.1",
    author="Csence",
    description="Unofficial API wrappper for Valorant",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/Csence/ValorantAPI_Wrapper",
    keywords=["Valorant", "Python", "API", "valorant-api"],
    project_urls={
        "Bug Tracker": "https://github.com/Csence/ValorantAPI_Wrapper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.0",
)