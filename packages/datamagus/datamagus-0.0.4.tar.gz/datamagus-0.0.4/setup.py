from distutils.core import setup
from setuptools import find_packages

setup(name='datamagus', 
      version='0.0.4', 
      description='Data analysis',
      long_description='Packages and API interface for basic data analysis\
         processing, graphing and modeling, and practical use.',
      author='alazia',
      author_email='alazia@email.com',
      url='https://github.com/Alazia/datamagus',
      license='Apache-2.0 license',
      install_requires=[
        'matplotlib>=3.3.2',
        'seaborn>=0.11.0',
        'numpy>=1.21.2',
        'pandas>=1.3.3',
        'flask>=1.1.4',
        'flasgger>=0.9.5'
      ],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.8',
          'Topic :: Utilities'
      ],
      keywords='',
      packages=find_packages('src'), 
      package_dir={'': 'src'},
      include_package_data=True,
      )
