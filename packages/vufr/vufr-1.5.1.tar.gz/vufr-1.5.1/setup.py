import os
from setuptools import find_packages, setup
from pip._internal.req import parse_requirements


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
req = ["requests==2.28.1"]
setup(
    name='vufr',
    version='1.5.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='A simple api wrapper for (shorten-url) vu.fr.',
    keywords='shorten-url shorten vu.fr',
    url='https://github.com/jiroawesome/vufr',
    author='JiroDeveloper',
    author_email='contact@jiroawesome.tech',
    install_requires=req,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ]
)