import ast
import codecs
import os
import re

import setuptools
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))


class VersionFinder(ast.NodeVisitor):
    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        if node.targets[0].id == '__version__':
            self.version = node.value.s


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*parts):
    finder = VersionFinder()
    finder.visit(ast.parse(read(*parts)))
    return finder.version


version = find_version('skies', '__init__.py')

install_requires = [
    'troposphere',
]

extras_require = {
    'tests': [
        'pytest >=2.6',
        'pytest-cov >=1.7,<2.0',
        'tox',
    ],
}

scripts = []

data_files = []


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


packages = setuptools.find_packages('.', exclude=('tests', 'tests.*'))
setuptools.setup(
    name='skies',
    version=version,
    url='https://github.com/mahmoudimus/skies',
    author='mahmoudimus',
    author_email='mabdelkader@gmail.com',
    description='A higher DSL for AWS Cloudformation',
    long_description='',
    platforms='any',
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require['tests'],
    packages=packages,
    scripts=[],
    data_files=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    cmdclass={'test': PyTest},
)
