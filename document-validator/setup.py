from setuptools import setup

setup(
    name='byteplug-document',
    version='0.1.2.dev3',
    description="Byteplug toolkit that implements the Document Validator standard.",
    url='https://www.byteplug.io/standards/document-validator',
    author='Jonathan De Wachter',
    author_email='jonathan.dewachter@byteplug.io',
    license='OSL-3.0',
    classifiers=[
        'License :: OSI Approved :: Open Software License 3.0 (OSL-3.0)'
    ],
    packages=['byteplug', 'byteplug.document'],
    namespace_packages = ['byteplug'],
    python_requires='>=3.9',
    install_requires=['pyyaml']
)
