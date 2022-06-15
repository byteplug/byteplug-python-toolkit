from setuptools import setup

setup(
    name='byteplug',
    version='0.1',
    description="The Byteplug toolkit for the Python programming language.",
    url='https://www.byteplug.io/',
    author='Jonathan De Wachter',
    author_email='jonathan.dewachter@byteplug.io',
    license='OSL-3.0',
    classifiers=[
        'License :: OSI Approved :: Open Software License 3.0 (OSL-3.0)'
    ],
    packages=['byteplug', 'byteplug.validator', 'byteplug.endpoints'],
    install_requires=[
        'pyyaml',
        'flask'
    ]
)
