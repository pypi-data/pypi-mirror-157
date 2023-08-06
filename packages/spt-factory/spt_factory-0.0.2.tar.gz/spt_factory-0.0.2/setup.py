#!/usr/bin/env python
from setuptools import find_namespace_packages, setup

package_name = "spt_factory"
package_version = "0.0.2"
description = """SPT resource manager"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author='Mark Poroshin',
    author_email='mporoshin@smartpredictiontech.ru',
    packages=find_namespace_packages(include=['spt_factory']),
    # url="https://gitlab.com/dv_group/dv_elt_lib",
    include_package_data=True,
    install_requires=[
        "psycopg2-binary==2.9.3",
        "pymongo==4.1.1"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
)
