#encoding:utf-8
import os
from setuptools import setup, find_packages

project_name = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

def read_file(filename):
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            filename)
    if os.path.exists(filepath):
        return open(filepath).read()
    else:
        return ''

setup(
    name=project_name,
    version="0.3.4",
    keywords=('sqlalchemy'),
    description="a tool for debug sqlalchemy model",
    long_description=read_file('README.rst'),
    platforms="any",
    install_requires=['SQLAlchemy>=1.0'],
    packages = find_packages()
)

