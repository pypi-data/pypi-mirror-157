#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import itertools
import yaml
import re
from typing import Dict, IO, List, Optional, Tuple, Union

def _istrue(tokens, name):
    """
    Helper that returns True if item named `name` is present in tokens
    and value is a YAML True value.
    """
    return name in tokens and yaml.safe_load(tokens[name]) == True

def _getvalue(tokens, name, default = None):
    if name in tokens: return tokens[name]
    return default

# TODO add additional parameter
def svtextparser_csv_wide(
    logfile: IO[str], tokens: Dict[str, str], delimiter=","
) -> Tuple[List[str], List[str]]:
    """
    Parses a 'wide' comma-separated value (CSV) file in the following format
    (whitespace is stripped):
    ```
    heading1, heading2,...
    value1,   value2, ...
    ```
    to `([heading1, heading2, ...], [value1, value2, ...])`.

    Any missing values are replaced by `None`. 
    Any additional value without a heading is given heading 
    `heading{column_index}` where column index starts from 1. If the token 
    `"parse_no_headings"` is set, all rows are used as
    values and all headings are genarated.

    If multiple rows of values are present, a suffix `_row{row_index}` is added 
    to all subsequent headings, where `row_index` starts from 2 for the second 
    values row.

    The token `"parse_delimiter"` will override the `delimiter` parameter, which
    is the delimiter that separates records in the file.

    Blank lines are skipped.

    This is a `svtext`-type parser as it uses the `csv` module.
    """
    if "parse_delimiter" in tokens:
        delimiter = tokens["parse_delimiter"]
    reader = csv.reader(logfile, delimiter=delimiter)

    if "parse_no_headings" in tokens:
        file_headings = []
    else:
        try:
            file_headings = [heading.strip() for heading in next(reader)]
        except StopIteration:
            file_headings = []
    out_headings = []
    out_values = []

    rows = []
    for row in reader:
        if len(row) == 0:
            continue  # skip blank lines
        rows.append(row)

    if len(rows) == 0:
        rows.append([])  # this ensures we have at least 1 row

    for row_index, row in enumerate(rows, start=1):
        suffix = f"_row{row_index}"
        for column, (file_heading, value) in enumerate(
            itertools.zip_longest(file_headings, row), start=1
        ):
            if value:
                value = value.strip()
            if file_heading is None:
                file_heading = f"heading{column}"
            if row_index == 1:
                out_heading = file_heading
            else:
                out_heading = file_heading + suffix
            out_headings.append(out_heading)
            out_values.append(value)
    return (out_headings, out_values)


def svtextparser_tsv_wide(
    logfile: IO[str], tokens: Dict[str, str]
) -> Tuple[List[str], List[str]]:
    """
    Parses a 'wide' tab-separated value (TSV) file in the following format
    (extra whitespace is stripped):
    ```
    heading1\t heading2\t...
    value1\t   value2\t ...
    ```
    to `{heading1: value1, heading2: value2, ...}`.

    See `pathparser_csv_wide()`.
    """
    return svtextparser_csv_wide(logfile, tokens, delimiter="\t")


def svtextparser_csv_tall(
    logfile: IO[str], tokens: Dict[str, str], delimiter=","
) -> Tuple[List[str], List[str]]:
    """
    Parses a 'tall' comma-separated value (CSV) file in the following format
    (whitespace is stripped):
    ```
    heading1, value1
    heading2, value2
    ...
    ```
    to `([heading1, heading2, ...], [value1, value2, ...])`.

    A row with only a single item is assumed to contain a heading alone, the 
    value is missing and replaced by `None`. If the token 
    `"parse_indiv_as_values"` is set (present and evaluates to a YAML `True`
    value, this behaviour is changed so that the item is the value and the 
    missing heading is given as `heading{row_index}`. If the token 
    `"parse_no_headings"` is set, all rows are used as values and all headings are 
    genarated.

    If multiple columns of values are present, a suffix `_col{col_index}` is added 
    to all subsequent headings, where `col_index` starts from 2 for the second 
    values column.

    The token `"parse_delimiter"` will override the delimiter parameter, which
    is the delimiter that separates records in the file.

    Blank lines are skipped.

    This is a `svtext`-type parser as it uses the `csv` module.
    """
    delimiter = _getvalue(tokens, "parse_delimiter", delimiter)
    indiv_as_values = _istrue(tokens, "parse_indiv_as_values")
    no_headings = _istrue(tokens, "parse_no_headings")
    parse_heading_strip = _getvalue(tokens, "parse_heading_strip") 
    parse_value_strip = _getvalue(tokens, "parse_value_strip") 

    reader = csv.reader(logfile, delimiter=delimiter)
    out_headings = []
    out_values = []

    for row_index, row in enumerate(reader, start=1):
        if len(row) == 0:
            row_index -= 1
            continue  # skip blank lines
        if no_headings or (len(row) == 1 and indiv_as_values):
            file_heading = f"heading{row_index}"
            values = row  # use all as values
        else:
            file_heading = row[0].strip(parse_heading_strip)
            values = row[1:]
            if len(values) == 0:
                values.append(None)  # this ensures we have at least 1 value

        for column, value in enumerate(values, start=1):
            if value:
                value = value.strip(parse_value_strip)
            if column == 1:
                out_heading = file_heading
            else:
                out_heading = file_heading + f"_row{column}"
            out_headings.append(out_heading)
            out_values.append(value)
    return (out_headings, out_values)


def svtextparser_tsv_tall(
    logfile: IO[str], tokens: Dict[str, str]
) -> Tuple[List[str], List[str]]:
    """
    Parses a 'tall' tab-separated value (TSV) file in the following format
    (extra whitespace is stripped):
    ```
    heading1\t value1
    heading2\t value2
    ...
    ```
    to `([heading1, heading2, ...], [value1, value2, ...])`.

    See `pathparser_csv_tall()`.
    """
    return svtextparser_csv_tall(logfile, tokens, delimiter="\t")

def textparser_regex(
    logfile: IO[str], tokens: Dict[str, str]
) -> Tuple[List[str], List[str]]:
    """
    Parses a generic text file using regular expressions to extract
    `heading: value` pairs from the file.
    
    Regular expressions are specified as tokens named `parse_re{name}` 
    with the regular expression given as their values. Regular expressions
    can either have named groups `heading` and `value`, which are used
    as the `heading` and `value` from parsing. If `heading` is not present,
    `{name}` in the regular expression is used as the `heading`, with up to
    two leading underscores stripped from this (so `parse_re_{name}` and
    `parse_re__{name}` will both give `{name}` as the heading). If named 
    group `value` is not present then the last capturing group in the regular 
    expression is used as the `value` (at least one capturing group must be
    specified in the regular expression). 
    
    In general, the regular expressions are processed for each line
    in the file looking for matches using the `re.match` function, but there 
    are additional options to change this behaviour.

    The following additional parameters can be provided to the parser. They
    should be specified as YAML-style boolean options to activate:

    `parse_multiline`: Apply regular expression as multiline regular expression.
    Activates the `MULTILINE` flag and uses the entire contents of file as
    a single string when matching. Note: This will trigger loading of the
    entire file into memory.

    `parse_ignorecase`: Activate `IGNORECASE` flag when matching regular 
    expressions.

    `parse_unicode`: Activate `UNICODE` flag when matching regular 
    expressions.

    `parse_search`: Use the `re.search` function to find matches.

    `parse_findall`: Find all matches for a regular expression, rather than just
    the first (uses `re.finditer` to find matches).
    """

    re_flags = 0
    use_multiline = _istrue(tokens, "parse_multiline")
    ignore_case = _istrue(tokens, "parse_ignorecase")
    use_unicode = _istrue(tokens, "parse_unicode")
    parse_search = _istrue(tokens, "parse_search")
    parse_findall = _istrue(tokens, "parse_findall")

    if use_multiline: re_flags |= re.MULTILINE
    if ignore_case: re_flags |= re.IGNORECASE
    if use_unicode: re_flags |= re.UNICODE

    regex_param_re = re.compile("^parse_regex_{0,2}(.*)$")

    re_list = []
    for token, value in tokens.items():
        token_match = regex_param_re.match(token)
        if token_match:
            re_heading = token_match.group(1)
            re_compiled = re.compile(value, re_flags)
            re_list.append((re_heading, re_compiled))
    
    if use_multiline:
        input_str = ""
        for line in logfile:
            input_str+=line
        lines = (input_str,)
    else:
        lines = logfile
    
    out_headings = []
    out_values = []
    for line in lines:
        for re_heading, re_compiled in re_list:
            if parse_findall:
                re_matches = re_compiled.finditer(line)
            else:
                if parse_search:
                    re_match = re_compiled.search(line)
                else:
                    re_match = re_compiled.match(line)
                re_matches = (re_match,)
            for re_match in re_matches:
                if re_match is None: continue
                match_groups = re_match.groupdict()
                if "heading" in match_groups:
                    out_heading = match_groups["heading"]
                else:
                    out_heading = re_heading
                if "value" in match_groups:
                    out_value = match_groups["value"]
                else:
                    if len(re_match.groups())<1:
                        raise Exception(f"{re_heading}: regular expression must have at least one capturing group")
                    out_value = re_match.groups()[-1]
                out_headings.append(out_heading)
                out_values.append(out_value)
    return (out_headings, out_values)
