from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='SHACL2SPARQLpy',
    version='1.0.0',
    packages=['S2Spy', 'S2Spy.constraints', 'S2Spy.core', 'S2Spy.sparql', 'S2Spy.utils'],
    license='MIT',
    author='Mónica Figuera, Philipp D. Rohde',
    author_email='philipp.rohde@tib.eu',
    url='https://github.com/SDM-TIB/S2Spy',
    download_url='https://github.com/SDM-TIB/S2Spy/archive/refs/tags/v1.0.0.tar.gz',
    description='Python reference implementation of SHACL2SPARQL',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['SPARQLWrapper>=1.8.5'],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research'
      ]
)
