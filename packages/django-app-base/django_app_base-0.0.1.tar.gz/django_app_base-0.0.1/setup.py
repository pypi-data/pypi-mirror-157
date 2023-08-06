from setuptools import setup
import re
import os

package = 'django_app_base'

requirements = [
    'Django>=2.0',
    'djangorestframework',
    'jsonfield'
]


def get_version():
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages():
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data():
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(
    name='django_app_base',
    version=get_version(),
    url='https://github.com/xunull/django-user-role',
    description='A django app for user role based permissions.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='xunull',
    packages=get_packages(),
    package_data=get_package_data(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
