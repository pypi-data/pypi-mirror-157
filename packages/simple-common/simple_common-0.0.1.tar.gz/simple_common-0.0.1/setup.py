from setuptools import setup, find_packages
import re
import os

package = 'simple_common'

requirements = [
    'pytz',
    'django',
    'dnspython'
]


def get_version():
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(
    name=package,
    version=get_version(),
    url='https://github.com/xunull/simple-common',
    description='some python code',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='xunull',
    packages=find_packages(exclude=("tests*",)),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
