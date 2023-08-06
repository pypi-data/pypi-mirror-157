import setuptools
from setuptools import Extension, dist, find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
      'torch==1.8.1',
      'scanpy==1.7.2',
      'anndata==0.7.6',
      'scipy>=1.6.2',
      'scikit-learn>=0.24.1',
      'numpy>=1.19.2',
      'pandas>=1.1.5',
      'statsmodels>=0.12.2',
      'louvain==0.7.0',
      'leidenalg==0.7.0',
      'umap-learn==0.4.6',
      'numba==0.49.1',
      'tables==3.6.1',
      'scikit-misc==0.1.3',
      'rpy2==3.4.5',
      'anndata2ri==1.0.6',
]
setup(name='portal-sc',
      version='1.0.2',
      description='An efficient, accurate and flexible method for single-cell data integration.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/YangLabHKUST/Portal',
      author='Jia Zhao',
      author_email='jzhaoaz@connect.ust.hk',
      license='MIT',
      packages=['portal'],
      install_requires=install_requires,
      zip_safe=False,
      python_requires='>=3.7',)