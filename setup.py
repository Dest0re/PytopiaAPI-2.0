from setuptools import setup, find_packages
import pytopia

setup(
    name=pytopia.__title__,
    version=pytopia.__version__,
    packages=find_packages(),
    author='Dest0re',
    description='',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ]
)
