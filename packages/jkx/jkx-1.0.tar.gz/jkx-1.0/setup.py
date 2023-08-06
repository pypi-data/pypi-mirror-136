from setuptools import setup, find_packages

setup(
    name='jkx',
    version='1.0',
    license='MIT',
    author="Andrew Heaney",
    author_email='heaneyandrew11@gmail.com',
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