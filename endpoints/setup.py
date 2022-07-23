from setuptools import setup

setup(
    name='byteplug-endpoints',
    version='0.1',
    description="Byteplug toolkit that implements the Endpoints standard.",
    url='https://www.byteplug.io/standards/endpoints',
    author='Jonathan De Wachter',
    author_email='jonathan.dewachter@byteplug.io',
    license='OSL-3.0',
    classifiers=[
        'License :: OSI Approved :: Open Software License 3.0 (OSL-3.0)'
    ],
    packages=['byteplug', 'byteplug.endpoints'],
    namespace_packages = ['byteplug']
)
