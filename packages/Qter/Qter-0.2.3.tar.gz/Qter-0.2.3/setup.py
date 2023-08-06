

import setuptools

from setuptools import setup

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='Qter',
    version='0.2.3',
    author='Subhash Shankar Pandey',
    author_email='subhashshankarpandeyy@gmail.com',
    description='A quantum simulator',
    long_description = long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Education',
        "Operating System :: OS Independent",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'

    ],
    keywords='Quantum_simulator',
    install_requires=[
        'numpy', 'matplotlib',   
    ],
)