from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text()

setup(
    name="la-catch",
    version="0.0.2",
    description="Decorator to map exception to functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thiagola92/la-catch",
    author="thiagola92",
    author_email="thiagola92@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords="decorator, exception, catch",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.10",
)
