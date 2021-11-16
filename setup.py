import setuptools
from ggseg import __version__


import os.path as op
this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setuptools.setup(
     name='ggseg',
     version=__version__,
     summary='Python module for ggseg-like visualizations',
     author='Greg Operto',
     author_email='goperto@barcelonabeta.org',
     url='https://github.com/ggseg/python-ggseg',
     packages=setuptools.find_packages(),
     description='Python module for ggseg-like visualizations',
     long_description=long_description,
     long_description_content_type='text/markdown',

     license='MIT',
     classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities',
          'Programming Language :: Python :: 3.8',
     ],
     install_requires=['matplotlib>=3.4',
                       'numpy>=1.21'],
     platforms='any',
     include_package_data=True
)
