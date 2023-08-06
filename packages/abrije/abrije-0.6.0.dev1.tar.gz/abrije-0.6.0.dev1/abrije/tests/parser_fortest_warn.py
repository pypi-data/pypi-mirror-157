#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict


def parser_blank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()


def rawparser_blank(infile) -> dict:
    """
    Parser of same name producing warning, for testing.
    """
    return OrderedDict()


# expected result of importing
expected_import_parser = {"blank": ("parser_blank", "text", parser_blank)}
