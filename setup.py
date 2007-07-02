import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension
import os
import sys
sys.path.insert(0, 'src')

version='0.0'
description="a simple validation framework"
long_description="""
validino is a simple validation framework with a functional
syntax.
"""
platforms="OS Independent"

keywords=["validation", "forms"]
classifiers=filter(None, """

Development Status :: 4 - Beta
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".split('\n'))

setup(author='Jacob Smullyan',
      author_email='jsmullyan@gmail.com',
      url='http://code.google.com/p/validino',
      description=description,
      long_description=long_description,
      keywords=keywords,
      platforms=platforms,
      license='MIT',
      name='validino',
      version=version,
      zip_safe=True,
      packages=['validino'],
      package_dir={'' : 'src'},
      test_suite='nose.collector',
      )
      
