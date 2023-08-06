from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name = "numericalintegratorr",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version = "0.0.1",
    author = "Xinyu Zhong",
    author_email = "zhong.xinyu@dhs.sg",
    description = ("Perform numerical integration"),
    license = "MIT",
    keywords = "numerical integration simpsons calculus",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)