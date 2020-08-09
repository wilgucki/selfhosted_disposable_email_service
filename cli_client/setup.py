#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    'Click==7.1.2',
    'tabulate==0.8.7',
]

setup(
    author="Mac",
    author_email='mwilgucki@gmail.com',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    description="Self-hosted disposable email service CLI client.",
    entry_points={
        'console_scripts': [
            'shdes=cli_client.cli:shdes',  # TODO this needs better name
        ],
    },
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    name='shdes',
    packages=find_packages(include=['cli_client', 'cli_client.*']),
    test_suite='tests',
    version='0.1.0',
    zip_safe=False,
)
