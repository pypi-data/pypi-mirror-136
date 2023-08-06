# ----------------------------------------------------------------------------------------------------------------------
# FILE DESCRIPTION
# ----------------------------------------------------------------------------------------------------------------------

# File:  setup.py
# Author:  Billy Carson
# Date written:  01-06-2022
# Last modified:  01-30-2022

"""
Description:  Setup Python file for beta-divergence-metrics library.
"""


# ----------------------------------------------------------------------------------------------------------------------
# IMPORT STATEMENTS
# ----------------------------------------------------------------------------------------------------------------------

# Import statements
import setuptools


# ----------------------------------------------------------------------------------------------------------------------
# SETUP
# ----------------------------------------------------------------------------------------------------------------------

with open('README.md', 'r', encoding='utf-8') as fh:
    readme_description = fh.read()

setuptools.setup(
    name='beta-divergence-metrics',
    version='0.0.2',
    author='Billy Carson',
    author_email='williamcarsoniv@gmail.com',
    description='NumPy and PyTorch implementations of the beta-divergence loss.',
    long_description=readme_description,
    long_description_content_type='text/markdown',
    keywords=[
        'numpybd',
        'torchbd',
        'numpy',
        'pytorch',
        'beta-divergence',
        'beta divergence',
        'beta',
        'divergence',
        'beta-loss',
        'beta loss',
        'loss',
        'beta-distance',
        'beta distance',
        'distance',
        'itakura-saito divergence',
        'itakura saito divergence',
        'is-divergence',
        'is divergence',
        'itakura-saito',
        'itakura saito',
        'itakura',
        'saito',
        'kullback-leibler divergence',
        'kullback leibler divergence',
        'kl divergence',
        'kl',
        'kullback-leibler',
        'kullback',
        'leibler',
    ],
    url='https://github.com/wecarsoniv/beta-divergence-metrics',
    project_urls={
        'Issue Tracker': 'https://github.com/wecarsoniv/beta-divergence-metrics/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
)

