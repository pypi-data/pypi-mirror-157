#
# File:    ./src/vutils/python/data.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2022-06-24 14:07:30 +0200
# Project: vutils-python: Python language tools
#
# SPDX-License-Identifier: MIT
#
"""Python data objects utilities."""

from typing import cast


def merge_data(dest: object, src: object) -> None:
    """
    Merge data from the source object to the destination object.

    :param dest: The destination object
    :param src: The source object
    :raises TypeError: when destination and source have different types
    """
    if not isinstance(dest, type(src)):
        raise TypeError("src and dest should have same types!")

    if isinstance(src, list):
        cast("list[object]", dest).extend(src)
    elif isinstance(src, set):
        cast("set[object]", dest).update(src)
    elif isinstance(src, dict):
        cast("dict[object, object]", dest).update(src)
    else:
        cast("dict[str, object]", dest.__dict__).update(
            cast("dict[str, object]", src.__dict__)
        )
