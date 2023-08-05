#  Copyright (c) 2022. Curie Zhang, Lanzhou Univ. of Tech.
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from setuptools import setup, find_packages

GFICLEE_VERSION = '2022.6.29.6'

setup(
    name='curiezhang-nester',
    version=GFICLEE_VERSION,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": ['curiezhang-nester = nester.main:main']
    },
    install_requires=[

    ],
    url='',
    license='GNU General Public License v3.0',
    author='curiezhang',
    author_email='zhjl@lut.edu.cn',
    description='More convenient to create fastapi project'
)
