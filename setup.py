#!/usr/bin/env python
from setuptools import setup, find_packages, Extension
from Cython.Distutils import build_ext
import sys
import os
import os.path
import numpy

incdirs=[numpy.get_include(),'include','pyx_src']


setup(name='MLTK-Qualia',
      version='0.1',
      description='Feature Extraction for Semantic Relations',
      author='Yannick Versley',
      author_email='versley@sfs.uni-tuebingen.de',
      cmdclass={'build_ext':build_ext},
      ext_modules=[Extension('mltk_qualia.content_extractor',
                             ['pyx_src/mltk_qualia/context_extractor.pyx'],
                             include_dirs=incdirs, language='c++',
                             define_macros=[('SGIext',None)])],
      entry_points = { 'console_scripts': [
            'bow_learn = mltk_qualia.bow_learn:main',
            'make_bigram_alph = mltk_qualia.make_bigram_alph:main',
            'compile_alphabets = mltk_qualia.task_config:compile_alphabets_main',
            'create_features = mltk_qualia.create_features:main']
                       },
      packages=['mltk_qualia'],
      package_dir={'':'py_src'}
      )

## numpy_setup(
##    ext_modules=[numpy_Extension('_lbfgs',['lbfgs/lbfgs.pyf','lbfgs/lbfgs.f'])]
##    )
                 
