from setuptools import setup
from pathlib import Path


# CHANGEME VARS
PACKAGE_NAME = 'nvna'
DESCRIPTION = 'NanoVNA python library'
AUTHOR_NAME = 'Florian Kolbl'
PROJECT_URL = "https://github.com/fkolbl/nvna"
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    # meta infos
    name=PACKAGE_NAME,
    author=AUTHOR_NAME,
    description=DESCRIPTION,
    url=PROJECT_URL,
    version="1.1.1",
    long_description=long_description,
    long_description_content_type='text/markdown',
    # architecture
    packages=[
        "nvna",
    ],

    include_package_data=True,
    # classifiers
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
    ],
    # dependencies 
    # * sorted by alphabetical order *
    install_requires=[
        "numpy",
        "pyserial",
    ],  # external packages as dependencies
    python_requires=">=3.12",
)
