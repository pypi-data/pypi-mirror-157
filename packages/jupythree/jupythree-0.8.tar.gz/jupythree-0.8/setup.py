
from setuptools import setup, find_packages


setup(
    name='jupythree',
    version='0.8',
    license='MIT',
    author="Raphaël Groscot",
    author_email='elgroscot@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/groscot/jupythree',
    keywords='example project',
    install_requires=[
          'numpy',
          'pythreejs',
          'matplotlib',
      ],

)