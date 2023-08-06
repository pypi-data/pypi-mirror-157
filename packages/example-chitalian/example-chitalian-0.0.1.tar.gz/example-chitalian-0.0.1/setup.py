from setuptools import setup, find_packages

setup(
    name='example-chitalian',
    version='0.0.1',
    packages=find_packages(include=['.*']),
    install_requires=[
        'betterproto>=2.0.0b4',
    ],
)
