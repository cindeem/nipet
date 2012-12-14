

from distutils.core import setup

setup(
    name='nipet',
    version='0.2.0',
    author='Cindee Madison',
    author_email='cindeem at gmail dot com',
    packages=['nipet', 'nipet.test'],
    license='LICENSE.txt',
    description='Tools for Graphical Analysis of PET data',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.6.1",
        ],
)
