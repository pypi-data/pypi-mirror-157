# -*- encoding: utf-8 -*-
import os
import setuptools
# from setuptools import find_packages, setup
# from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setuptools.setup(
    name='easy-audit-farrux',
    version='0.0.1',
    # packages=find_packages(),
    packages=['easyauditfarrux'],
    include_package_data=True,
    install_requires=[
        "beautifulsoup4",
        "django>=2.2,<5.0"
    ],
    python_requires=">=3.5",
    license='GPL3',
    description='Yet another Django audit log app, hopefully the simplest one.',
    long_description=README,
    url='https://github.com/suyunovfarrux4544/django-easy-audit-farrux.git',
    author='Suyunov Farrux',
    author_email='suyunovfarrux4544@gmail.com',
    classifiers=[
        'Environment :: Plugins',
        'Framework :: Django',
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
