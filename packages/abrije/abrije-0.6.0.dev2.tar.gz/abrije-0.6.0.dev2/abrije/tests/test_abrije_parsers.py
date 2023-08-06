#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import io
from collections import OrderedDict

from abrije.parsers import *
from abrije.abrije import NamedTokens


csvwide_test1 = "heading1,heading2,heading3\nvalue1,value2,value3"
csvwide_test1a = "heading1, heading2 ,heading3\n value1  ,\tvalue2\t, value3"
csvwide_test1b = " heading1 ,\theading2 ,heading3   \n value1\t,value2, value3 "
csvwide_test1c = "heading1,heading2,heading3\nvalue1,value2,value3\n"
csvwide_test1d = (
    "heading1\theading2\theading3\nvalue1\tvalue2\tvalue3"  # "parse_delimiter": "\t"
)
csvwide_test1e = "value1,value2,value3"  # "parse_no_headings" : "yes"
csvwide_expected1 = (
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvwide_test2 = "heading1,heading2,heading3\nvalue1"
csvwide_expected2 = (
    ["heading1", "heading2", "heading3"],
    ["value1", None, None],
)
csvwide_test3 = "headingA,headingB\nvalue1,value2,value3"
csvwide_expected3 = (
    ["headingA", "headingB", "heading3"],
    ["value1", "value2", "value3"],
)
csvwide_test4 = "heading1,heading2,heading3\n"
csvwide_test4a = "heading1,heading2,heading3\n\n"
csvwide_expected4 = (
    ["heading1", "heading2", "heading3"],
    [None, None, None],
)
csvwide_test5 = "heading1,heading2,heading3\nvalue1,value2,value3\nvalue4,value5"
csvwide_expected5 = (
    [
        "heading1",
        "heading2",
        "heading3",
        "heading1_row2",
        "heading2_row2",
        "heading3_row2",
    ],
    ["value1", "value2", "value3", "value4", "value5", None],
)
csvwide_test6 = "heading1,heading2,heading3\nvalue1,value2,value3\n,\n"
csvwide_expected6 = (
    [
        "heading1",
        "heading2",
        "heading3",
        "heading1_row2",
        "heading2_row2",
        "heading3_row2",
    ],
    ["value1", "value2", "value3", "", "", None],
)
csvwide_test7 = (
    "heading1,heading2,heading3\nvalue1,value2,value3\n\n"  # extra newline skipped
)
csvwide_test7a = (
    "heading1,heading2,heading3\n\nvalue1,value2,value3\n"  # extra newline skipped
)
csvwide_expected7 = (
    ["heading1", "heading2", "heading3",],
    ["value1", "value2", "value3"],
)
csvwide_test8 = "heading1,heading2,heading3\nvalue1,value2,value3"
csvwide_expected8a = ( # "heading_prefix": "pre"
    ["preheading1", "preheading2", "preheading3"],
    ["value1", "value2", "value3"],
)
csvwide_expected8b = ( # "heading_suffix": "suf"
    ["heading1suf", "heading2suf", "heading3suf"],
    ["value1", "value2", "value3"],
)
csvwide_expected8c = ( # "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", "prevalue3"],
)
csvwide_expected8d = ( # "value_suffix": "suf"
    ["heading1", "heading2", "heading3"],
    ["value1suf", "value2suf", "value3suf"],
)
csvwide_test9 = " heading1 ,\theading2\t,heading3\n value1 ,\tvalue2\t,value3"
csvwide_expected9a = ( # default, whitespace stripped
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvwide_expected9b = ( # "parse_heading_strip" : ""
    [" heading1 ", "\theading2\t", "heading3"],
    ["value1", "value2", "value3"],
)
csvwide_expected9c = ( # "parse_value_strip" : ""
    ["heading1", "heading2", "heading3"],
    [" value1 ", "\tvalue2\t", "value3"],
)
csvwide_expected9d = ( # "parse_heading_strip" : "h3"
    [" heading1 ", "\theading2\t", "eading"],
    ["value1", "value2", "value3"],
)
csvwide_expected9e = ( # "parse_value_strip" : "v3"
    ["heading1", "heading2", "heading3"],
    [" value1 ", "\tvalue2\t", "alue"],
)
csvwide_test10 = "heading1,heading2,heading3\nvalue1,value2"
csvwide_expected10a = ( # default: missing becomes None
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", None],
)
csvwide_expected10b = ( # "parse_value_missing": "value3"
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvwide_expected10c = ( # "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", None],
)
csvwide_expected10d = ( # parse_value_missing: "value3", "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", "prevalue3"],
)



@pytest.mark.parametrize(
    "test_input,test_tokens,expected",
    [
        (csvwide_test1, {}, csvwide_expected1),
        (csvwide_test1a, {}, csvwide_expected1),
        (csvwide_test1b, {}, csvwide_expected1),
        (csvwide_test1c, {}, csvwide_expected1),
        (csvwide_test1d, {"parse_delimiter": "\t"}, csvwide_expected1),
        (csvwide_test1e, {"parse_no_headings": "yes"}, csvwide_expected1),
        (csvwide_test2, {}, csvwide_expected2),
        (csvwide_test3, {}, csvwide_expected3),
        (csvwide_test4, {}, csvwide_expected4),
        (csvwide_test4a, {}, csvwide_expected4),
        (csvwide_test5, {}, csvwide_expected5),
        (csvwide_test6, {}, csvwide_expected6),
        (csvwide_test7, {}, csvwide_expected7),
        (csvwide_test8, {"heading_prefix": "pre"}, csvwide_expected8a),
        (csvwide_test8, {"heading_suffix": "suf"}, csvwide_expected8b),
        (csvwide_test8, {"value_prefix": "pre"}, csvwide_expected8c),
        (csvwide_test8, {"value_suffix": "suf"}, csvwide_expected8d),
        (csvwide_test9, {}, csvwide_expected9a),
        (csvwide_test9, {"parse_heading_strip" : ""}, csvwide_expected9b),
        (csvwide_test9, {"parse_value_strip" : ""}, csvwide_expected9c),
        (csvwide_test9, {"parse_heading_strip" : "h3"}, csvwide_expected9d),
        (csvwide_test9, {"parse_value_strip" : "v3"}, csvwide_expected9e),
        (csvwide_test10, {}, csvwide_expected10a),
        (csvwide_test10, {"parse_value_missing": "value3"}, csvwide_expected10b),
        (csvwide_test10, {"value_prefix": "pre"}, csvwide_expected10c),
        (csvwide_test10, {"parse_value_missing": "value3", "value_prefix": "pre"},
            csvwide_expected10d),

    ],
)
def test_parser_csv_wide(test_input, test_tokens, expected):

    expected_result = NamedTokens.fromLists(*expected)
    with io.StringIO(test_input) as handle:
        result = NamedTokens.fromLists(
            *svtextparser_csv_wide(handle, tokens=test_tokens)
        )
        assert result == expected_result


@pytest.mark.parametrize(
    "test_input,test_tokens,expected",
    [
        (csvwide_test1d, {}, csvwide_expected1),
        (csvwide_test1, {"parse_delimiter": ","}, csvwide_expected1),
        (csvwide_test1b, {"parse_delimiter": ","}, csvwide_expected1),
    ],
)
def test_parser_tsv_wide(test_input, test_tokens, expected):

    expected_result = NamedTokens.fromLists(*expected)
    with io.StringIO(test_input) as handle:
        result = NamedTokens.fromLists(
            *svtextparser_tsv_wide(handle, tokens=test_tokens)
        )
        assert result == expected_result


csvtall_test1 = "heading1,value1\nheading2,value2\nheading3,value3"
csvtall_test1a = " heading1,value1\t\nheading2\t,value2\nheading3,value3"
csvtall_test1b = "heading1  ,value1  \nheading2   ,value2\n heading3\t,value3   "
csvtall_test1c = "heading1,value1\nheading2,value2\nheading3,value3\n"
csvtall_test1d = (
    "heading1\tvalue1\nheading2\tvalue2\nheading3\tvalue3"  # "parse_delimiter": "\t"
)
csvtall_test1e = "value1\nvalue2\nvalue3"  # "parse_no_headings" : "yes"
csvtall_expected1 = (
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvtall_test2 = "heading1,value1\nheading2\nheading3\n"
csvtall_expected2 = (
    ["heading1", "heading2", "heading3"],
    ["value1", None, None],
)
csvtall_test3 = "headingA,value1\nheadingB,value2\nvalue3"
csvtall_expected3 = (  # without "parse_indiv_as_values"
    ["headingA", "headingB", "value3"],
    ["value1", "value2", None],
)
csvtall_expected3a = (  # "parse_indiv_as_values" : "yes"
    ["headingA", "headingB", "heading3"],
    ["value1", "value2", "value3"],
)
csvtall_test4 = "heading1\nheading2\nheading3\n"
csvtall_test4a = "heading1\nheading2\nheading3\n\n"
csvtall_expected4 = (
    ["heading1", "heading2", "heading3"],
    [None, None, None],
)
csvtall_test5 = "heading1,value1,value4\nheading2,value2,value5\nheading3,value3"
csvtall_expected5 = (
    ["heading1", "heading1_row2", "heading2", "heading2_row2", "heading3"],
    ["value1", "value4", "value2", "value5", "value3"],
)
csvtall_test6 = "heading1,value1,\nheading2,value2,\nheading3,value3"
csvtall_expected6 = (
    ["heading1", "heading1_row2", "heading2", "heading2_row2", "heading3"],
    ["value1", "", "value2", "", "value3"],
)
csvtall_test7 = (
    "heading1,value1\nheading2,value2\nheading3,value3\n\n"  # extra newline skipped
)
csvtall_test7a = (
    "heading1,value1\n\nheading2,value2\nheading3,value3\n"  # extra newline skipped
)
csvtall_expected7 = (
    ["heading1", "heading2", "heading3",],
    ["value1", "value2", "value3"],
)
csvtall_test8 = "heading1,value1\nheading2,value2\nheading3,value3"
csvtall_expected8a = ( # "heading_prefix": "pre"
    ["preheading1", "preheading2", "preheading3"],
    ["value1", "value2", "value3"],
)
csvtall_expected8b = ( # "heading_suffix": "suf"
    ["heading1suf", "heading2suf", "heading3suf"],
    ["value1", "value2", "value3"],
)
csvtall_expected8c = ( # "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", "prevalue3"],
)
csvtall_expected8d = ( # "value_suffix": "suf"
    ["heading1", "heading2", "heading3"],
    ["value1suf", "value2suf", "value3suf"],
)
csvtall_test9 = " heading1 , value1 \n\theading2\t,\tvalue2\t\nheading3,value3"
csvtall_expected9a = ( # default, whitespace stripped
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvtall_expected9b = ( # "parse_heading_strip" : ""
    [" heading1 ", "\theading2\t", "heading3"],
    ["value1", "value2", "value3"],
)
csvtall_expected9c = ( # "parse_value_strip" : ""
    ["heading1", "heading2", "heading3"],
    [" value1 ", "\tvalue2\t", "value3"],
)
csvtall_expected9d = ( # "parse_heading_strip" : "h3"
    [" heading1 ", "\theading2\t", "eading"],
    ["value1", "value2", "value3"],
)
csvtall_expected9e = ( # "parse_value_strip" : "v3"
    ["heading1", "heading2", "heading3"],
    [" value1 ", "\tvalue2\t", "alue"],
)
csvtall_test10 = "heading1,value1\nheading2,value2\nheading3"
csvtall_expected10a = ( # default: missing becomes None
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", None],
)
csvtall_expected10b = ( # "parse_value_missing": "value3"
    ["heading1", "heading2", "heading3"],
    ["value1", "value2", "value3"],
)
csvtall_expected10c = ( # "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", None],
)
csvtall_expected10d = ( # parse_value_missing: "value3", "value_prefix": "pre"
    ["heading1", "heading2", "heading3"],
    ["prevalue1", "prevalue2", "prevalue3"],
)


@pytest.mark.parametrize(
    "test_input,test_tokens,expected",
    [
        (csvtall_test1, {}, csvtall_expected1),
        (csvtall_test1a, {}, csvtall_expected1),
        (csvtall_test1b, {}, csvtall_expected1),
        (csvtall_test1c, {}, csvtall_expected1),
        (csvtall_test1d, {"parse_delimiter": "\t"}, csvtall_expected1),
        (csvtall_test1e, {"parse_no_headings": "yes"}, csvtall_expected1),
        (csvtall_test2, {}, csvtall_expected2),
        (csvtall_test3, {}, csvtall_expected3),
        (csvtall_test3, {"parse_indiv_as_values": "yes"}, csvtall_expected3a),
        (csvtall_test4, {}, csvtall_expected4),
        (csvtall_test4a, {}, csvtall_expected4),
        (csvtall_test5, {}, csvtall_expected5),
        (csvtall_test6, {}, csvtall_expected6),
        (csvtall_test7, {}, csvtall_expected7),
        (csvtall_test8, {"heading_prefix": "pre"}, csvtall_expected8a),
        (csvtall_test8, {"heading_suffix": "suf"}, csvtall_expected8b),
        (csvtall_test8, {"value_prefix": "pre"}, csvtall_expected8c),
        (csvtall_test8, {"value_suffix": "suf"}, csvtall_expected8d),
        (csvtall_test9, {}, csvtall_expected9a),
        (csvtall_test9, {"parse_heading_strip" : ""}, csvtall_expected9b),
        (csvtall_test9, {"parse_value_strip" : ""}, csvtall_expected9c),
        (csvtall_test9, {"parse_heading_strip" : "h3"}, csvtall_expected9d),
        (csvtall_test9, {"parse_value_strip" : "v3"}, csvtall_expected9e),
        (csvtall_test10, {}, csvtall_expected10a),
        (csvtall_test10, {"parse_value_missing": "value3"}, csvtall_expected10b),
        (csvtall_test10, {"value_prefix": "pre"}, csvtall_expected10c),
        (csvtall_test10, {"parse_value_missing": "value3", "value_prefix": "pre"},
            csvtall_expected10d),
    ],
)
def test_parser_csv_tall(test_input, test_tokens, expected):

    expected_result = NamedTokens.fromLists(*expected)
    with io.StringIO(test_input) as handle:
        result = NamedTokens.fromLists(
            *svtextparser_csv_tall(handle, tokens=test_tokens)
        )
        assert result == expected_result


@pytest.mark.parametrize(
    "test_input,test_tokens,expected",
    [
        (csvtall_test1d, {}, csvtall_expected1),
        (csvtall_test1, {"parse_delimiter": ","}, csvtall_expected1),
        (csvtall_test1b, {"parse_delimiter": ","}, csvtall_expected1),
    ],
)
def test_parser_tsv_tall(test_input, test_tokens, expected):

    expected_result = NamedTokens.fromLists(*expected)
    with io.StringIO(test_input) as handle:
        result = NamedTokens.fromLists(
            *svtextparser_tsv_tall(handle, tokens=test_tokens)
        )
        assert result == expected_result
