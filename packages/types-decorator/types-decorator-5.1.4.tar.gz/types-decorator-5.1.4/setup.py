from setuptools import setup

name = "types-decorator"
description = "Typing stubs for decorator"
long_description = '''
## Typing stubs for decorator

This is a PEP 561 type stub package for the `decorator` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `decorator`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/decorator. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `0e185f40877a614c5ddd87815707cf8153296872`.
'''.lstrip()

setup(name=name,
      version="5.1.4",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['decorator-stubs'],
      package_data={'decorator-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
