from setuptools import (
    setup,
    find_packages
)
from leo import _config


def read_file(fname):
    with open(fname, 'r') as ftext:
        return ftext.read()

setup(
    name='leo',
    version='1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'aiohttp'
    ],

    url='http://github.com/nkthanh98/leo',
    author='Nguyen Khac Thanh',
    author_email='nguyenkhacthanh244@gmail.com',
    license='MIT',
    description='LEO - Command line for synchronous data',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    python_requires='>3.5.2',
    entry_points=f'''
        [console_scripts]
        {_config.LEO_COMMAND}=leo:cli
    ''',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Command Line :: E-Paper',
    ],
)
