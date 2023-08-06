from setuptools import setup
import sys

if sys.version_info < (3, 7):
    raise RuntimeError("Python >= 3.7")

setup(
    name="probarly",
    version="1.0.1",
    description="Create beautiful, heavily customizable progress bars... probarly",
    url="http://github.com/phil-gates/probarly",
    author="Phil",
    author_email="mateopw10@gmail.com",
    license="MIT",
    packages=["probarly"],
    zip_safe=False,
    classifiers=["Programming Language :: Python :: 3.7"],
)
