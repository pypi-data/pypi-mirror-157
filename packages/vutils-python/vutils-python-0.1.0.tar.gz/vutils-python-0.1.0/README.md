[![Coverage Status](https://coveralls.io/repos/github/i386x/vutils-python/badge.svg?branch=main)](https://coveralls.io/github/i386x/vutils-python?branch=main)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/i386x/vutils-python.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/i386x/vutils-python/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/i386x/vutils-python.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/i386x/vutils-python/context:python)

# vutils-python: Python Language Tools

This package provides a set of tools to deal with tasks related to Python
language environment, like copying data to or from objects, importing, object
analysis etc.

## Installation

To get `vutils-python`, just type
```sh
$ pip install vutils-python
```

## How To Use

Functions and classes provided by `vutils-python` can be accessed by importing
following submodules:
* `vutils.python.data`

Each of these submodules is described in the following subsections.

### Data Objects Manipulation

Functions and classes that deals with Python data objects, defined in
`vutils.python.data` submodule, are
* `merge_data(dest, src)` merges data from `src` to `dest`. `src` and `dest`
  must be of the same type. Examples:
  ```python
  src = [1, 2, 3]
  dest = [1, 2]
  merge_data(dest, src)
  # dest will be [1, 2, 1, 2, 3]

  src = {1, 2, 3}
  dest = {2, 4}
  merge_data(dest, src)
  # dest will be {1, 2, 3, 4}

  src = {"a": "bc", 1: 2}
  dest = {1: "a", "b": "c"}
  merge_data(dest, src)
  # dest will be {1: 2, "a": "bc", "b": "c"}

  merge_data({}, [1])  # TypeError
  ```
