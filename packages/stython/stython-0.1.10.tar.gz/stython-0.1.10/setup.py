from setuptools import setup, find_packages

readme = open('README.txt', "r").read()
license = open('LICENSE.txt', "r").read()
stython = find_packages()

setup(
    name='stython',
    version='0.1.10',
    description='Stython package',
    long_description=readme,
    author='Arun Kapila',
    author_email='starshootercity@gmail.com',
    url='https://github.com/cometcake575/stython',
    license=license,
    packages=stython
)