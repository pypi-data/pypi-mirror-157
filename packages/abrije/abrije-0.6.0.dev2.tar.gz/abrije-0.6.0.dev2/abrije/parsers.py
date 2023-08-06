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

def svtextparser_csv_wide(
    logfile: IO[str], tokens: Dict[str, str], delimiter=","
) -> Tuple[List[str], List[Union[str, None]]]:
    """
    Parses a 'wide' comma-separated value (CSV) file in the following format
    (whitespace is stripped):
    ```
    heading1, heading2,...
    value1,   value2, ...
    ```
    to `([heading1, heading2, ...], [value1, value2, ...])`.

    Any missing values are replaced by `None` (by default). 
    Any additional value without a heading is given heading 
    `heading{column_index}` where column index starts from 1. If the token 
    `"parse_no_headings"` is set, all rows are used as
    values and all headings are generated.
    `parse_heading_strip` and `parse_value_strip` are the character sets used
    for stripping from both sides of headings values; if unset defaults to
    stripping whitespace. Set to `""` to strip no characters.
    `parse_value_missing` is  used as the value when value is missing; 
    defaults to `None`. Can be an empty string to ensure prefix/suffix are 
    always added.
    `heading_suffix` and `heading_prefix` are the suffix and prefix added to
    all headings; this is final step before storing so all other processing is
    performed before these are added to the heading.
    `value_suffix` and `value_prefix` are the suffix and prefix added to
    all values; this is final step before storing so all other processing is
    performed before these are added to the value but requires that the 
    value is not `None`.

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

    parse_heading_strip = tokens.get("parse_heading_strip") 
    parse_value_strip = tokens.get("parse_value_strip") 
    parse_value_missing = tokens.get("parse_value_missing") 

    heading_suffix = tokens.get("heading_suffix", "")
    heading_prefix = tokens.get("heading_prefix", "")
    value_suffix = tokens.get("value_suffix", "")
    value_prefix = tokens.get("value_prefix", "")

    if "parse_no_headings" in tokens:
        file_headings = []
    else:
        try:
            file_headings = [
                heading.strip(parse_heading_strip)
                for heading in next(reader)]
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
        row_suffix = f"_row{row_index}"
        for column, (file_heading, value) in enumerate(
            itertools.zip_longest(file_headings, row), start=1
        ):
            if value is None:
                value = parse_value_missing
            else:
                value = value.strip(parse_value_strip)

            if file_heading is None:
                file_heading = f"heading{column}"
            if row_index == 1:
                out_heading = file_heading
            else:
                out_heading = file_heading + row_suffix
            out_headings.append(heading_prefix + out_heading + heading_suffix)
            out_values.append(value if value is None else \
                value_prefix + value + value_suffix)
    return (out_headings, out_values)


def svtextparser_tsv_wide(
    logfile: IO[str], tokens: Dict[str, str]
) -> Tuple[List[str], List[Union[str, None]]]:
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
) -> Tuple[List[str], List[Union[str, None]]]:
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
    value is missing and replaced by `None` (by default). If the token 
    `"parse_indiv_as_values"` is set (present and evaluates to a YAML `True`
    value, this behaviour is changed so that the item is the value and the 
    missing heading is given as `heading{row_index}`. If the token 
    `"parse_no_headings"` is set, all rows are used as values and all headings are 
    genarated.
    `parse_heading_strip` and `parse_value_strip` are the character sets used
    for stripping from both sides of headings values; if unset defaults to
    stripping whitespace. Set to `""` to strip no characters.
    `parse_value_missing` is  used as the value when value is missing; 
    defaults to `None`. Can be an empty string to ensure prefix/suffix are 
    always added.
    `heading_suffix` and `heading_prefix` are the suffix and prefix added to
    all headings; this is final step before storing so all other processing is
    performed before these are added to the heading.
    `value_suffix` and `value_prefix` are the suffix and prefix added to
    all values; this is final step before storing so all other processing is
    performed before these are added to the value but requires that the 
    value is not `None`.

    If multiple columns of values are present, a suffix `_col{col_index}` is added 
    to all subsequent headings, where `col_index` starts from 2 for the second 
    values column.

    The token `"parse_delimiter"` will override the delimiter parameter, which
    is the delimiter that separates records in the file.

    Blank lines are skipped.

    This is a `svtext`-type parser as it uses the `csv` module.
    """
    delimiter = tokens.get("parse_delimiter", delimiter)
    indiv_as_values = _istrue(tokens, "parse_indiv_as_values")
    no_headings = _istrue(tokens, "parse_no_headings")

    parse_heading_strip = tokens.get("parse_heading_strip") 
    parse_value_strip = tokens.get("parse_value_strip") 
    parse_value_missing = tokens.get("parse_value_missing") 

    heading_suffix = tokens.get("heading_suffix", "")
    heading_prefix = tokens.get("heading_prefix", "")
    value_suffix = tokens.get("value_suffix", "")
    value_prefix = tokens.get("value_prefix", "")

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
            if value is None:
                value = parse_value_missing
            else:
                value = value.strip(parse_value_strip)
            if column == 1:
                out_heading = file_heading
            else:
                out_heading = file_heading + f"_row{column}"
            out_headings.append(heading_prefix + out_heading + heading_suffix)
            out_values.append(value if value is None else \
                value_prefix + value + value_suffix)
    return (out_headings, out_values)


def svtextparser_tsv_tall(
    logfile: IO[str], tokens: Dict[str, str]
) -> Tuple[List[str], List[Union[str, None]]]:
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
) -> Tuple[List[str], List[Union[str, None]]]:
    """
    Parses a generic text file using regular expressions to extract
    `heading: value` pairs from the file.
    
    Regular expressions are specified as tokens named `parse_regex{name}` 
    with the regular expression given as their values. Regular expressions
    can either have named groups `heading*` and `value*`, which are used
    to derive the `heading` and `value` from parsing. If multiple groups 
    starting with `heading` or `value` are present, the group names are sorted
    and the resulting `heading` or `value` is derived by joining all groups
    with `heading_sep` or `value_sep` (default: `""`). If an underscore (`_`)
    is present in the group name, then the contents after the underscore
    are used as the group value, instead of the captured string itself.
    
    If `heading*` is not present, 
    `{name}` in the regular expression is used as the `heading`, with up to
    two leading underscores stripped from this (so `parse_regex_{name}` and
    `parse_regex__{name}` will both give `{name}` as the heading). If no named 
    group `value*` is not present then the last capturing group in the regular 
    expression is used as the `value` (at least one capturing group must be
    specified in the regular expression). 

    `heading_suffix` and `heading_prefix` are the suffix and prefix added to
    all headings; this is final step before storing so all other processing is
    performed before these are added to the heading.
    `value_suffix` and `value_prefix` are the suffix and prefix added to
    all values; this is final step before storing so all other processing is
    performed before these are added to the value.

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

    heading_sep = tokens.get("heading_sep", "")
    heading_suffix = tokens.get("heading_suffix", "")
    heading_prefix = tokens.get("heading_prefix", "")
    value_sep = tokens.get("value_sep", "")
    value_suffix = tokens.get("value_suffix", "")
    value_prefix = tokens.get("value_prefix", "")

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
                re_tokens_headings = {}
                re_tokens_values = {}
                for key,value in match_groups.items():
                    if "_" in key:
                        token = key.split("_",1)[1]
                    else:
                        token = value
                    if key.startswith("heading"):
                        re_tokens_headings[key] = token
                    if key.startswith("value"):
                        re_tokens_values[key] = token

                if re_tokens_headings:
                    out_heading = heading_sep.join(re_tokens_headings[key] for key in sorted(re_tokens_headings.keys()))
                else:
                    out_heading = re_heading
                if re_tokens_values:
                    out_value = value_sep.join(re_tokens_values[key] for key in sorted(re_tokens_values.keys()))
                else:
                    if len(re_match.groups())<1:
                        raise Exception(f"{re_heading}: regular expression must have at least one capturing group")
                    out_value = re_match.groups()[-1]
                
                out_headings.append(heading_prefix + out_heading + heading_suffix)
                out_values.append(value_prefix + out_value + value_suffix)
    return (out_headings, out_values)
