import re
import numpy
#from distutils.core import setup, Extension
from setuptools import setup, Extension

VERSIONFILE='src/_version.py'
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

module = Extension('Marsh', 
                   sources = ['src/c-code/OptimalExtraction/Marsh.c'], 
                   libraries=['gsl', 'gslcblas', 'm'], 
                   include_dirs=[numpy.get_include(),'/usr/local/include'])

setup(name='transitspectroscopy',
      version=verstr,
      description='transitspectroscopy: a library for all your transit spectroscopy needs',
      url='http://github.com/nespinoza/transitspectroscopy',
      author='Nestor Espinoza',
      author_email='nespinoza@stsci.edu',
      license='MIT',
      packages=['transitspectroscopy'],
      package_dir={'transitspectroscopy': 'src'},
      install_requires=['numpy','scipy'],
      python_requires='>=3.0',
      ext_modules = [module],
      zip_safe=False)
