from setuptools import setup, find_packages


with open('README.txt') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='stython',
    version='0.1.1',
    description='Stython package',
    long_description=readme,
    author='Arun Kapila',
    author_email='starshootercity@gmail.com',
    url='https://github.com/cometcake575/stython',
    license=license,
    packages=find_packages()
)

