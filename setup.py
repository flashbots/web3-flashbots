from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='web3_flashbots',
    version='0.1.0',
    description='Flashbots plugin for Web3.py',
    long_description=readme,
    author='Georgios Konstantopoulos',
    author_email='me@gakonst.com',
    url='https://github.com/gakonst/web3-flashbots',
    license="MIT",
    packages=find_packages(exclude=('tests', 'docs'))
)
