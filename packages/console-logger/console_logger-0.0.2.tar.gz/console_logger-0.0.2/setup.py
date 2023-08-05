from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='console_logger',
    version='0.0.2',
    packages=['console_logger'],
    url='https://github.com/BuchnevM/console_logger',
    license='MIT License',
    author='Mikhail Buchnev',
    author_email='me@buchnev.page',
    description='Yet another logging package for Python',
    long_description=long_description,
    long_description_content_type="text/markdown"
)
