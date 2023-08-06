#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict


def parser_blank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()


parser_notcallable = "a string"
# 'parser' that is not a function, produces error, for testing

# expected result of importing
expected_import_parser = {"blank": ("parser_blank", "text", parser_blank)}
