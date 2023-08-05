from setuptools import setup, find_packages

setup(
    name="datamanipy",
    version="1.2.4",
    author="Alexandre Le Potier",
    description="A Python package that provides tools to help you manipulating data.",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include="datamanipy.*"),
    python_requires=">=3.9",
    install_requires=[
        'sqlalchemy>=1.4.28',
        'pandas>=1.3.5',
        'keyring>=23.5.0',
        'pyreadstat>=1.1.4',
        'openpyxl>=3.0.10',
        'datetime>=4.3'],
    long_description="""
# datamanipy

## What is it?

**datamanipy** is a Python package that provides tools to help you manipulating data.

## Where to get it?

The source code is currently hosted on [GitHub](https://github.com/alplepot/datamanipy).
Distribution files are available on PyPI.

```sh
# install datamanipy from PyPI
pip install datamanipy
```

## Dependencies

- [sqlalchemy](https://docs.sqlalchemy.org/en/14/)
- [pandas](https://pandas.pydata.org/)
- [keyring](https://keyring.readthedocs.io)
- [pyreadstat](https://pyreadstat.readthedocs.io)
- [openpyxl](https://openpyxl.readthedocs.io)
- [datetime](https://docs.python.org/3/library/datetime.html)

## Contributing to art

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.
        """,
    long_description_content_type='text/markdown',
)
