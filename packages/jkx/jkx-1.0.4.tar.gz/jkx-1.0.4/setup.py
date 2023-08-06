from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='jkx',
    version='1.0.4',
    license='MIT',
    author="Andrew Heaney",
    author_email='heaneyandrew11@gmail.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'jkx=jkx.main:start'
        ]
    },
    packages=['jkx'],
    url='https://github.com/AndrewHeaney/json-key-explorer',
    keywords='json',
    install_requires=[
          'inquirer',
      ],

)