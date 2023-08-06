#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from collections import OrderedDict

from abrije.abrije import Abrije


class TestAbrijeClass:
    def test_add_parser(self):
        abrije_ = Abrije()  # test object
        parser_null = lambda handle: None  # dummy parsers for testing
        rawparser_null = lambda handle: None
        pathparser_null = lambda path: None

        # test add parser of default type: text
        abrije_.add_parser("parser_test", parser_null)
        expected_add_parser = {"test": ("parser_test", "text", parser_null)}
        assert abrije_.parsers == expected_add_parser

        # test adding parser of various types: text, raw, path
        abrije_.add_parser("textparser_test1", parser_null)
        abrije_.add_parser("svtextparser_test1a", parser_null)
        abrije_.add_parser("rawparser_test2", rawparser_null)
        abrije_.add_parser("pathparser_test3", pathparser_null)
        expected_add_parser.update(
            {
                "test1": ("textparser_test1", "text", parser_null),
                "test1a": ("svtextparser_test1a", "svtext", parser_null),
                "test2": ("rawparser_test2", "raw", rawparser_null),
                "test3": ("pathparser_test3", "path", pathparser_null),
            }
        )
        assert abrije_.parsers == expected_add_parser

        # test exception on adding unsupported type
        with pytest.raises(ValueError, match="unknown type"):
            abrije_.add_parser("strangeparser_test", parser_null)

        # test silent ignore parser of wrong name format
        prev_parsers = abrije_.parsers.copy()
        abrije_.add_parser("ignored", parser_null)
        abrije_.parsers
        assert abrije_.parsers == prev_parsers

        # test warning on add parser of same name
        # and no new parser added
        prev_parsers = abrije_.parsers.copy()
        with pytest.warns(UserWarning, match="same name"):
            abrije_.add_parser("rawparser_test", parser_null)
        assert abrije_.parsers == prev_parsers

        # test exception on adding non-callable func
        with pytest.raises(ValueError, match="not callable"):
            abrije_.add_parser("parser_test4", "a string")

    def test_import_parsers(self):

        # test import from module
        abrije_ = Abrije()  # test object
        import abrije.tests.parser_fortest  # module must be imported first

        abrije_.import_parsers(abrije.tests.parser_fortest)
        assert abrije_.parsers == abrije.tests.parser_fortest.expected_import_parser

        abrije_ = Abrije()  # reset test object
        import abrije.tests.parser_fortest_warn

        with pytest.warns(UserWarning, match="same name"):
            abrije_.import_parsers(abrije.tests.parser_fortest_warn)
        assert (
            abrije_.parsers == abrije.tests.parser_fortest_warn.expected_import_parser
        )

        abrije_ = Abrije()  # reset test object
        import abrije.tests.parser_fortest_err1

        with pytest.raises(ValueError, match="unknown type"):
            abrije_.import_parsers(abrije.tests.parser_fortest_err1)
        assert (
            abrije_.parsers == abrije.tests.parser_fortest_err1.expected_import_parser
        )

        abrije_ = Abrije()  # reset test object
        import abrije.tests.parser_fortest_err2

        with pytest.raises(ValueError, match="not callable"):
            abrije_.import_parsers(abrije.tests.parser_fortest_err2)
        assert (
            abrije_.parsers == abrije.tests.parser_fortest_err2.expected_import_parser
        )

        # test import from list
        # make some dummy parsers for testing
        def rawparser_null(handle):
            return OrderedDict()

        def pathparser_none(path):
            return OrderedDict()

        expected_import_parser_list = {
            "null": ("rawparser_null", "raw", rawparser_null),
            "none": ("pathparser_none", "path", pathparser_none),
        }

        abrije_ = Abrije()  # reset test object
        toadd_list = [rawparser_null, pathparser_none]
        abrije_.import_parsers(toadd_list)
        assert abrije_.parsers == expected_import_parser_list

        # test import from tuple
        abrije_ = Abrije()  # reset test object
        toadd_tuple = (rawparser_null, pathparser_none)
        abrije_.import_parsers(toadd_tuple)
        assert abrije_.parsers == expected_import_parser_list

        # test import from dict
        abrije_ = Abrije()  # reset test object
        toadd_dict = {
            # use different names
            "parser_test1": rawparser_null,
            "pathparser_test2": pathparser_none,
        }

        expected_import_parser_dict = {
            "test1": ("parser_test1", "text", rawparser_null),
            "test2": ("pathparser_test2", "path", pathparser_none),
        }
        abrije_.import_parsers(toadd_dict)
        assert abrije_.parsers == expected_import_parser_dict

        # test import combined
        abrije_ = Abrije()  # reset test object
        expected_import_parser_combined = (
            abrije.tests.parser_fortest.expected_import_parser
        )
        expected_import_parser_combined.update(expected_import_parser_list)
        expected_import_parser_combined.update(expected_import_parser_dict)

        abrije_.import_parsers(abrije.tests.parser_fortest)
        abrije_.import_parsers(toadd_list)
        abrije_.import_parsers(toadd_dict)
        assert abrije_.parsers == expected_import_parser_combined

        # test re-import, causing warnings for same name
        with pytest.warns(UserWarning, match="same name"):
            abrije_.import_parsers(toadd_list)
        assert abrije_.parsers == expected_import_parser_combined
