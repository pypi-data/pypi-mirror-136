
from setuptools import setup, find_packages
from os import path
import pathlib

here = pathlib.Path(__file__).parent.resolve()
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sentence_pass",
    version=0.2,
    description="Generate password from a sentence",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages('sen_pass'),
    author='Huyen Le'
)