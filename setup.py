#!/usr/bin/env python

from setuptools import setup
import pry

CLASSIFIERS = [
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Natural Language :: English",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "Topic :: Software Development :: Debuggers",
]

setup(
    name='pry.py',
    version=pry.module.VERSION,
    classifiers=CLASSIFIERS,
    description='Pry ruby-like interactive shell, written in Python',
    author='Joerg Thalheim',
    author_email='joerg@thaleheim.io',
    url='https://github.com/Mic92/pry.py',
    license="MIT License",
    py_modules=['pry'],
    zip_safe=True,
)
