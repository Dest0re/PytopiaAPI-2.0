from setuptools import setup, find_packages
import pytopiaAPI

setup(
    name=pytopiaAPI.__title__,
    version=pytopiaAPI.__version__,
    packages=find_packages(),
    author='Dest0re',
    description='',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ]
)
