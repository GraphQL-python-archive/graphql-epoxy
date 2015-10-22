from setuptools import setup, find_packages

setup(
    name='graphql-epoxy',
    version='0.0.0dev',
    description='GraphQL implementation for Python',
    url='https://github.com/graphql-python/graphql-core',
    download_url='https://github.com/graphql-python/graphql-core/releases',
    author='Jake Heinz',
    author_email='me' '@' 'jh.gg',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License',
    ],

    keywords='api graphql protocol rest',
    packages=find_packages(exclude=['tests']),
    install_requires=['graphql-core>=0.4.7b0'],
    tests_require=['pytest>=2.7.3'],
)
