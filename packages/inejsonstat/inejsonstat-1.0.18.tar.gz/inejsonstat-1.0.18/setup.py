from setuptools import setup
from setuptools import find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='inejsonstat',
    version='1.0.18',
    packages=find_packages(),
    install_requires=['inejsonstat',
    'numpy',
    'requests',
    'terminaltables',
    'click',
    'cython',
    'pandas',
    'aenum',
    'pyyaml',
    'unidecode',
    'datetime'],
    package_data={'': ['config.yaml','inejsonstat.log']},
    include_package_data=True,
    url='https://github.com/Mlgpigeon/inejsonstat.git',
    license='MIT License',
    author='Luis María Salete Cuartero',
    author_email='luismasc16@gmail.com',
    description='Library to interact with the INE JSON-Stat API',
    long_description=long_description,
    long_description_content_type="text/markdown"
)
