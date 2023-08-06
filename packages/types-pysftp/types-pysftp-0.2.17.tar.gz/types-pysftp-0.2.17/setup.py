from setuptools import setup

name = "types-pysftp"
description = "Typing stubs for pysftp"
long_description = '''
## Typing stubs for pysftp

This is a PEP 561 type stub package for the `pysftp` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `pysftp`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/pysftp. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8ef6602e25d563146d3f513f9201d927ec31c07e`.
'''.lstrip()

setup(name=name,
      version="0.2.17",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/pysftp.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-paramiko'],
      packages=['pysftp-stubs'],
      package_data={'pysftp-stubs': ['__init__.pyi', 'exceptions.pyi', 'helpers.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
