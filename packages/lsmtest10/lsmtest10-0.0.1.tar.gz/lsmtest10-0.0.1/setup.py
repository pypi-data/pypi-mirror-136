# coding=utf-8
# Copyright 2022 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Setup script for installing large_scale_mmdma as a pip module."""
import os
from setuptools import find_packages
from setuptools import setup

folder = os.path.dirname(__file__)
# Reads the version
__version__ = None
with open(os.path.join(folder, "lsmmdma/version.py")) as f:
  exec(f.read(), globals())

readme_path = os.path.join(folder, "README.md")
readme_contents = ""
if os.path.exists(readme_path):
  with open(readme_path) as fp:
    readme_contents = fp.read().strip()


setup(
    name="lsmtest10",
    version=__version__,
    description="Scaling MMD-MA.",
    author="Google LLC",
    author_email="lpapaxanthos@google.com",
    url="https://github.com/google-research/large_scale_mmdma",
    long_description=readme_contents,
    long_description_content_type="text/markdown",
    license="Apache 2.0",
    packages=find_packages(),
    package_data={},
    install_requires=['absl-py', 'numpy>=1.19', 'torch>=1.10',
                      'tensorflow-cpu>=2.7', 'pykeops==1.5',
                      'typing==3.7.4.3', 'dataclasses==0.6',
                      'cmake==3.18', 'setuptools>=59.5.0',
                      'tenacity>=8.0', 'sklearn'],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    keywords="kernel, data integration",
    requires_python=">=3.6",
)


