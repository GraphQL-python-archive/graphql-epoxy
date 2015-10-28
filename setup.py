from setuptools import setup, find_packages
import sys

required_packages = ['graphql-core>=0.4.7b1']

if sys.version_info <= (2, 7, 0):
    required_packages.append('enum34>=1.0.4')

if sys.version_info <= (3, 4, 0):
    required_packages.append('singledispatch>=3.4.0')

setup(
    name='graphql-epoxy',
    version='0.2a1',
    description='GraphQL implementation for Python',
    url='https://github.com/graphql-python/graphql-core',
    download_url='https://github.com/graphql-python/graphql-core/releases',
    author='Jake Heinz',
    author_email='me' '@' 'jh.gg',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
    ],

    keywords='api graphql protocol rest',
    packages=find_packages(exclude=['tests']),
    install_requires=required_packages,
    tests_require=['pytest>=2.7.3'],
)
