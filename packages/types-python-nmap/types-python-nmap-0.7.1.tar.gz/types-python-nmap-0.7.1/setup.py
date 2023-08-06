from setuptools import setup

name = "types-python-nmap"
description = "Typing stubs for python-nmap"
long_description = '''
## Typing stubs for python-nmap

This is a PEP 561 type stub package for the `python-nmap` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `python-nmap`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/python-nmap. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8ef6602e25d563146d3f513f9201d927ec31c07e`.
'''.lstrip()

setup(name=name,
      version="0.7.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/python-nmap.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['nmap-stubs'],
      package_data={'nmap-stubs': ['__init__.pyi', 'nmap.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
