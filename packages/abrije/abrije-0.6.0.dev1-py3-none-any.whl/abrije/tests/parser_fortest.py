#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

def parser_blank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()

def ignored(infile) -> dict:
    """
    Ignored function, for testing.
    """
    return OrderedDict()

def textparser_textblank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()

def rawparser_rawblank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()

def pathparser_pathblank(infile) -> dict:
    """
    Parser that does nothing, for testing.
    """
    return OrderedDict()

# expected result of importing
expected_import_parser = {
    'blank' : ('parser_blank', 'text', parser_blank),
    'textblank' : ('textparser_textblank', 'text', textparser_textblank),
    'rawblank' : ('rawparser_rawblank', 'raw', rawparser_rawblank),
    'pathblank' : ('pathparser_pathblank', 'path', pathparser_pathblank)
}
