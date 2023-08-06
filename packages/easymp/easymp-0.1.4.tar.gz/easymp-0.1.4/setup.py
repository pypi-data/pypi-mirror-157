from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="easymp",
    version="0.1.4",
    description="Python utility for easy multiprocessing + logging.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="0BSD",
    author="MNayer",
    author_email="marie.nayer@web.de",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/MNayer/easymp",
    keywords="multiprocessing logging",
    install_requires=[],
)
