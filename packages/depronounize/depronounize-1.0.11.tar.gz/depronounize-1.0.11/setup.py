
from setuptools import setup, find_packages


setup(
    name="depronounize",
    version='1.0.11',
    description="Pronoun replacement module",
    url="https://github.com/NazarTrilisky/PronounReplacement",
    install_requires=["spacy"],
    include_package_data=True,
    zip_safe=False,
    author_email="",
    license="MIT",
    author="Nazar Trilisky",
    packages=find_packages()
)

