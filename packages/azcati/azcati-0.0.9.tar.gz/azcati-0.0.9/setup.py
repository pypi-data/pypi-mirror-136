from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

VERSION = '0.0.9' 
DESCRIPTION = 'Arizona Center for Algae Technology & Innovation Cloud Database Library'
LONG_DESCRIPTION = long_description

setup(
        name="azcati", 
        version=VERSION,
        author="Evan Taylor",
        author_email="evan.taylor@asu.edu",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        packages=find_packages(),
        install_requires=['boto3', 'pandas'], 
        setup_requires=['wheel'],
        keywords=['miprobe', 'labprobe', 'algae', 'ASU', 'AzCATI'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Science/Research",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: POSIX :: Linux",
            "Operating System :: POSIX :: BSD :: FreeBSD",
            "License :: OSI Approved :: MIT License",
        ],
        url='https://gitlab.com/evantaylor/azcati-cloud'
)
