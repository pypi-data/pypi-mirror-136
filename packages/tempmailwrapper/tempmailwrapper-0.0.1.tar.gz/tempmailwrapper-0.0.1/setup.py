from setuptools import setup, find_packages
import os

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


LONG_DESCRIPTION = read('README.md')

setup(
    name="tempmailwrapper",
    version="0.0.1",
    author="Jimballoons",
    author_email="jimballoonsgit@gmail.com",
    description="API wrapper for Temp Mail API.",
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests',],
    keywords=['python', 'tempmail', 'temporary', 'email', 'wrapper',],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)