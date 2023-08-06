from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='arithmetic_calc',
    version='0.1',
    description='Arithmetic Calculator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ibsa Abraham',
    author_email='ibsaabraham663@gmail.com',
    packages=['arithmetic_calc'],
    zip_safe = False
)