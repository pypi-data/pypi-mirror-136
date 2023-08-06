# ---------------------------------------------------------------------------------
# Pyomo Solver Wrapper
# Language - Python
# https://github.com/judejeh/PyomoSolverWrapper
# Licensed under MIT license
# Copyright 2021 The Pyomo Solver Wrapper authors <https://github.com/judejeh>
# ---------------------------------------------------------------------------------

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as rdm:
    long_description = rdm.read()

setup(name='PyoSolveWrapper',
      packages=['PyoSolveWrapper'],
      version='0.3.2',
      description='Wrapper for Pyomo solve method',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/judejeh/PyomoSolverWrapper',
      download_url='https://github.com/judejeh/PyomoSolverWrapper/archive/refs/tags/v0.3.1.tar.gz',
      author='Jude Ejeh, Solomon F. Brown',
      author_email='joe@judejeh.com',
      license='MIT',
      python_requires='>=3.5',
      install_requires=[
          'pyomo <= 6.0.1',
          'numpy',
          'pyutilib >= 5.7.3'
        ],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ],
      zip_safe=False)