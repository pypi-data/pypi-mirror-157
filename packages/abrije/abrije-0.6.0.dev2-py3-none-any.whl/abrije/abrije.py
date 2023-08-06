#!/usr/bin/env python
# -*- coding: utf-8 -*-

# uses Google docstrings: https://google.github.io/styleguide/pyguide.html
# (numpy-style not supported in multi-line returns docstrings with type hints)
# use typehints, not in docstrings

"""
abrije
======

abrije is a generic log parser and summariser.

A user provides ``abrije`` with a list of `logset`s to parse. Each `logset`
consists of name, a snakemake-style path pattern, a type to specify method
of parsing the log file, and parameters to go with the parser. A general
config can also be provided to give defaults for all `logset`s. 

Old (out-of-date) docs follow:

To process input files, ``abrije`` will test each regex sequential until it
finds one that matches the input file path (as determined by the glob). Named
groups with the regex provide required or optional info to ``abrije``. All
named groups should be in the format ``prefixSUFFIX__providedcontents`` or
``prefix_SUFFIX__providedcontents``. SUFFIX and providedcontents are usually
optional. Unless otherwise noted, providedcontents simply replaces the contents captured by the
regex to provide additional flexibility.
The
following prefixes are possible, each serving a different purpose:

    1) label : This prefix is used for given the input file a label. Multiple
    levels of label are possible, these will be sorted by label name before
    the contents (i.e. text captured by the regex or providedcontents) is combined into a 'full_label' separated by '>' characters. Since the
    label names are sorted, it is useful to provide numbered suffixes to these
    (e.g. label_1run, label2_sample to give Run129>Sample141) so the ordering is clearly specified.
    Data from all input files that have the same full_label are combined into
    a single output row. At least one label is required.

    2) type : This prefix is used to specify the file type for the input file
    which determines the parser used to process the file. A parser is simply
    a Python function that takes a file handle as single parameter, and returns
    an OrderedDict of data column_heading:value. If a suffix is provided, it is used
    as the file type, otherwise the captured contents of the regex is used. The
    providedcontents does not override the capture contents, and instead provides
    additional input settings in the format setting1_IS_value1_AND_setting2_IS_value2.
    Currently, the only input setting available is 'encoding' which specifies the
    input encoding of the file (overriding the default script option). An additional
    'encoding' provided by ``abrije`` is 'binary' which causes the input file
    to be opened in binary mode, instead of text mode.

    3) tag : tags are used to 'tag' the columns read from the input file. It is
    useful to use this when multiple files of the same type are present for the
    same full_label (e.g. different steps). Tagging allows the data from each
    file to be given a unique column heading. Each tag is in the added in the format
    SUFFIX=contents, or simply the SUFFIX or contents if the other is absent. Multiple
    tags are separated by commas, and all tags are prepended to the original column heading
    followed by a '>'.

    4) comment : comment specifies additional columns prepended to any input from
    the data file. The column heading is SUFFIX (or 'comment' if absent), and the contents
    are the value. All comment columns are also tagged.

    ``abrije`` locates the function as
    type_parse() in predefined parsers or a module that is imported using the


Working from a directory tree, the
A list of globs and regexes

list of globs. Used to locate input files.

Each glob is used by ``abrije`` to build a list of input files to parse.

list of regexes. Used to provide metadata and tell abrije how to parse the file.
The path of each input file is tested against each regex for a match. Upon
finding a match (i.e. the first matching regex is used), the named groups
within the regex are used as follows:
label, labelXXXX, or label_XXXX = used for grouping log files
type, typeXXXX, or type_XXXX = used for specifying log type, former group content gives type, otherwise use XXXX
tag, tagXXXX, or tag_XXXX = used to tag log data in heading, former tags with 'tagged', otherwise tag with XXXX
comment, commentXXXX or comment_XXXX
first underscore before XXXX ignored
labelXXXX__YYYY YYYY used as content instead of group_contents

provide ``abrije`` with key data about the file
# provide list of regex
#  how to match regex to file? simplest would be to use first regex that matches
# regex has named groups
#  label or label_x -> used to match data to a line
#  type or type_xxx
#    if group name is type, group match gives type_name
#    otherwise, group name gives is type_name(xxx); actual match ignored, allows regex definition to define type, as filename may not have discernable type
#    used to define the parser, will call type_parse(file)
#    expected to return a dict containing headings>data
#  tag_xxxx
#   tags headings with xxxx (group match value ignored)
#  other groups tag headings with groupname=value
#

 path of each input file is tested against each regex for a match.


plugins can use logger 'abrije'
"""


###
# smart parse files
# provide list of files
# provide list of regex
#  how to match regex to file? simplest would be to use first regex that matches
# regex has named groups
#  label or label_x -> used to match data to a line
#  type or type_xxx
#    if group name is type, group match gives type_name
#    otherwise, group name gives is type_name(xxx); actual match ignored, allows regex definition to define type, as filename may not have discernable type
#    used to define the parser, will call type_parse(file)
#    expected to return a dict containing headings>data
#  tag_xxxx
#   tags headings with xxxx (group match value ignored)
#  other groups tag headings with groupname=value
#

import csv
import re
import pathlib
import glob
import importlib
import argparse
import sys
import logging
import pprint
import traceback
import os
import warnings
import typing
import json
import yaml

from collections import OrderedDict, defaultdict, namedtuple
from types import ModuleType
from typing import (
    Callable,
    Dict,
    IO,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

try:  # workaround for Python<3.7, no typing.OrderedDict
    typing.OrderedDict
except AttributeError:
    typing.OrderedDict = typing.MutableMapping


import snakemake.utils 
try:
    import abrije.parsers
except:
    # this allows importing abrije.parsers even when run as a script
    import parsers
    class Namespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    abrije = Namespace(parsers=parsers)

import io


_PROGRAM_NAME = "abrije"
_PROGRAM_VERSION = "0.6.0.dev2"


# INIT LOGGING
# logging, create a stderr and stdout handler
logger = logging.getLogger(_PROGRAM_NAME)  #: Module logger.
logger.setLevel(logging.DEBUG)  # top-level logs everything

stderr_handler = logging.StreamHandler(sys.stderr)
"""
Logging handler to `stderr`, `WARNING` and above.
"""
logger.addHandler(stderr_handler)
stderr_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
stderr_handler.setFormatter(stderr_formatter)
stderr_handler.setLevel(logging.WARNING)

stdout_handler = logging.StreamHandler(sys.stdout)
"""
Logging handler to `stdout`, controlled by verbosity.
"""
logger.addHandler(stdout_handler)
stdout_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
stdout_handler.setFormatter(stdout_formatter)

# warning handling
def warning(msg: str) -> None:
    logger.warning(msg)
    warnings.warn(msg)


# integration between logging and warnings not used as this logs to separate
# logger
# warnings.simplefilter("always")
# logging.captureWarnings(True)  # integrate with warnings.warn
# py_warnings_logger = logging.getLogger("py.warnings")
# py_warnings_logger.addHandler(stdout_handler)
# py_warnings_logger.addHandler(stderr_handler)

_DEBUG: bool = False  #: `True` enables traceback.
_verbose: int = 0  #: Controls output to `stdout` handler.


def set_verbosity(verbose: Optional[int]) -> None:
    """
    Set logging verbosity to stdout:
    `2` : `DEBUG` and enables traceback.
    `1` : `INFO`.
    `0` : `CRITICAL`.
    """
    global _verbose, _DEBUG
    if verbose is None:
        verbose = 0
    _verbose = verbose
    _DEBUG = False
    if _verbose >= 2:
        stdout_handler.setLevel(logging.DEBUG)
        _DEBUG = True
        # if verbosity is debug, traceback of handled exceptions will be output as logger.error
    elif _verbose >= 1:
        stdout_handler.setLevel(logging.INFO)
    elif _verbose >= 0:
        stdout_handler.setLevel(logging.CRITICAL)


set_verbosity(2)

# pretty formatter, wrap in object so not called unless needed
pformat = pprint.PrettyPrinter(indent=2, width=120).pformat


class PrettyLog:
    def __init__(self, obj):
        self.obj = obj

    def __repr__(self):
        # if isinstance(self.obj,OrderedDict):
        # special handling for OrderedDict, as not handled by pformat by default
        #    return pformat([(key,value) for (key,value) in self.obj.items()])
        # pprint SEEMS to work in Python 3.6
        return pformat(self.obj)


ParserFunc = Callable[
    [Union[IO[str], IO[bytes], str], Dict[str, str]], Tuple[List[str], List[str]]
]
"""
Parsers are in the form `parser(handle_or_path, tokens)` where `handle_or_path`
is the input file handle or path and `tokens` is a `dict` of tokens for the
log file. Parsers should return a tuple `(headings, values)` where `headings`
and `values` are lists.
"""

StoredParser = Tuple[str, str, ParserFunc]
"""
Parser details stored as `(fullname, type, function)`.
"""

TNamedTokens = TypeVar("TNamedTokens", bound="NamedTokens")


class NamedTokens:
    """
    A simple class that maintains parallel lists of `headings` and `values`.

    Ideally created from factory methods `new()` and `fromLists()`.
    """

    def __init__(self, headings: List[str], values: List[str]) -> None:
        self.headings: List[str] = headings  #: List of `headings`.
        self.values: List[str] = values  #: List of `values`.

    @classmethod
    def new(cls, heading: str = None, value: str = None) -> TNamedTokens:
        """
        Create a new `NamedTokens` object, with optional first values; object
        starts empty otherwise.

        Args:
            heading: First `headings` value.
            value: First `values` value.

        Returns:
            A new `NamedTokens` object.
        """
        obj = NamedTokens([], [])
        if heading is not None:
            assert value is not None, "both heading and value should be provided"
            obj.append(heading, value)
        return obj

    @classmethod
    def fromLists(cls, headings: List[str], values: List[str]) -> TNamedTokens:
        """
        Create a new `NamedTokens` object from the provided `headings` and 
        `values` lists. The provided lists are used directly by the new object
        and may be mutated by the object; they should only be mutated externally
        with care to avoid corrupting the `NamedTokens` object using them.

        Args:
            headings: List of `headings` for this object.
            values: List of `values` for this object. Should be same length as
                `headings`.

        Returns:
            A new `NamedTokens` object.
        """
        assert len(headings) == len(
            values
        ), "headings and values should be the same size"
        return NamedTokens(headings, values)

    def append(self, heading: str, value: str) -> None:
        """
        Append `heading` and `value` to this object.

        Args:
            heading: The `headings` value to append.
            value: The `values` value to append.
        """
        self.headings.append(heading)
        self.values.append(value)

    def extend(self, items: Iterable[Tuple[str, str]]) -> None:
        """
        Extend this object with additional `headings` and `values`.

        Args:
            items: An iterable yielding tuples of `(heading, value)` to add to
                this object.
        """
        for heading, value in items:
            self.headings.append(heading)
            self.values.append(value)

    def tag_headings(self, prefix: str) -> None:
        """
        Tag headings by prepending `prefix` to each.

        Args:
            prefix: Prefix to add to each heading.
        """
        for i, heading in enumerate(self.headings):
            self.headings[i] = prefix + heading

    def render_values(self) -> str:
        """
        Convert contents to `heading1:value1, heading2:value2, ...`.

        Returns:
            `heading1:value1, heading2:value2, ...`.
        """
        return ", ".join(f"{heading}:{value}" for heading, value in self)

    def has_redundant_headings(self) -> bool:
        """
        Check if any `headings` are identical.

        Returns:
            `True` if there are any identical headings, `False` otherwise.
        """
        return len(self.headings) > len(set(self.headings))

    def make_headings_unique(self) -> None:
        """
        Makes all headings unique by adding `(x)` as suffix where `x` is an 
        increasing number from 2 until a unique heading is found.
        """
        existing = {}

        for i, heading in enumerate(self.headings):
            suffix_index = 2
            newheading = heading
            while newheading in existing:
                newheading = f"{heading} ({suffix_index})"
                suffix_index += 1
            self.headings[i] = newheading
            existing[newheading] = True

    def __len__(self) -> int:
        return len(self.headings)

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        return zip(self.headings, self.values)

    def __repr__(self) -> str:
        return (
            "{" + ", ".join(f"'{heading}':'{value}'" for heading, value in self) + "}"
        )

    def __eq__(self, o: object) -> bool:
        if isinstance(o, NamedTokens):
            return self.headings == o.headings and self.values == o.values
        else:
            return NotImplemented

# TODO: implicitly expects tokens to be an OrderedDict. Is this guaranteed? Perhaps in python 3.7+
# (Implementation detail in python 3.6)
def filter_tokens(source: TNamedTokens, tokens: Dict[str, str]) -> TNamedTokens:
    _istrue = lambda tokens, name: name in tokens and yaml.safe_load(tokens[name]) == True
    _getvalue = lambda tokens, name, default = None: tokens[name] if name in tokens else default

    re_flags = 0
    ignore_case = _istrue(tokens, "filter_ignorecase")
    use_unicode = _istrue(tokens, "filter_unicode")
    filter_search = _istrue(tokens, "filter_search")
    filter_default_exclude = _istrue(tokens, "filter_default_exclude")

    if ignore_case: re_flags |= re.IGNORECASE
    if use_unicode: re_flags |= re.UNICODE

    regex_param_re = re.compile("^filter_(exclude|include).*$")

    re_list = []
    for token, value in tokens.items():
        token_match = regex_param_re.match(token)
        if token_match:
            filter_exclude = token_match.group(1)=="exclude"
            re_compiled = re.compile(value, re_flags)
            re_list.append((filter_exclude, re_compiled))

    print(re_list)
    obj = NamedTokens.new()
    for heading, value in source:
        exclude = filter_default_exclude
        for filter_exclude, re_compiled in re_list:
            if filter_search:
                re_match = re_compiled.search(heading)
            else:
                re_match = re_compiled.match(heading)
            if re_match:
                exclude = filter_exclude
        if not exclude: obj.append(heading, value)
    return obj

class AbrijeConfig:
    """
    Class for storing config used when processing `log_set`s with `abrije`.

    A separate class is used to facilitate a nested defaults (for all `log_sets`)/
    override config for a particular `log_set`.

    Args:
    config_set: Name of this config set.

    """

    wildcard_param_regex = re.compile("^{(.+)}$")
    """
    Wildcard parameters are specified as `{wildcard_name}`.
    """

    def __init__(self, config_set: str):
        self.config_set: str = config_set
        """
        Name of this config set.
        """

        self.wildcard_mapping: Optional[Dict[str, str]] = None
        """
        Stores mapping of `wildcard_name -> token_name` where `token_name` is
        a `label_name` or `tag_name` identifier used to determine what the
        token value (wildcard contents) should be used for by `abrije`,
        e.g. `'sample' -> 'label1_samplename'`.
        """

        self.const_mapping: Optional[Dict[str, str]] = None
        """
        Stores mapping of `token_name -> token_value` to give a constant 
        `token_value` for the given `token_name`. Constants have precedence
        over wildcards with the same `token_name`.
        e.g. `'label1_samplename' -> 'Sample140'`
        """

        self.overrides: Optional[Dict[str, AbrijeConfig]] = None
        """
        Stores mapping of `log_set -> override_config` where 
        `override_config` is the (optional) config for a specific
        `log_set`.
        """

    def add_to_config(
        self, parameters=Dict[str, str], log_set: Optional[str] = None
    ) -> None:
        """
        Adds `parameters` to this object (if `log_set` is `None`) or to the
        override config for given `log_set`.

        Args:
            parameters: `dict` of `param_name -> param_value`.  Wildcard 
                parameters are specified as `{wildcard_name}` in the 
                `param_name`, all others (without curly brackets) are 
                considered const parameters.
            log_set: Name of `log_set` if these are for override config of that 
                `log_set`.
        """

        if log_set == "defaults":
            raise ValueError("add_to_config: log_set = defaults should not be used")
        assert (
            log_set != self.config_set
        ), "add_to_config: log_set should not be passed to overrides"

        if log_set is None:
            for param_name, param_value in parameters.items():
                wildcard_param_match = self.wildcard_param_regex.match(param_name)
                if wildcard_param_match:
                    # wildcard param
                    if not self.wildcard_mapping:
                        self.wildcard_mapping = {}
                    wildcard_param_name = wildcard_param_match.group(1)
                    self.wildcard_mapping[wildcard_param_name] = param_value
                    logger.debug(
                        f"Added wildcard parameter {wildcard_param_name}:{param_value} "
                        f"to {self.config_set}"
                    )
                else:
                    # const param
                    if not self.const_mapping:
                        self.const_mapping = {}
                    self.const_mapping[param_name] = param_value
                    logger.debug(
                        f"Added const parameter {param_name}:{param_value} "
                        f"to {self.config_set}"
                    )

        else:
            if not self.overrides:
                self.overrides = {}
            abrije_config = self.overrides.setdefault(log_set, AbrijeConfig(log_set))
            abrije_config.add_to_config(parameters)

    def resolve_tokens(
        self,
        log_set: Optional[str],
        wildcards: Optional[Dict[str, str]],
        cur_tokens: Optional[Dict[str, str]] = None,
        consumed_wildcards: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, str], Optional[Set[str]]]:
        """
        Resolve all wildcard or const parameter tokens.

        Args:
            log_set: Name of the `log_set` to resolve for; used to detect any 
                overrides. May be `None`, in which case no overrides are 
                resolved.

            wildcards: Wildcards as `dict` of `wildcard_name -> wildcard_value` 
                used to resolve any wildcard parameters. May be `None`, in which 
                case only const tokens are resolved.

            cur_tokens: A `dict` of any tokens already resolve; new tokens are 
                added to this if provided, replacing any existing tokens of the 
                same name.

            consumed_wildcards: A `set` of any wildcards already consumed; if
                provided, any additional wildcards that are consumed when 
                resolving are added to this.


        Returns:
            `(param_dict, consumed_wildcards_set)` where param_dict is a `dict`
            of `param_name -> param_value` and `consumed_wildcards_set` is a
            `set` of all wildcards that were consumed when resolving tokens.
            These will be the same as the parameters `cur_tokens` and
            `consumed_wildcards` if provided. `consumed_wildcards_set` will be 
            `None` if `wildcards` was `None`.

        """
        if cur_tokens is None:
            cur_tokens = {}

        if wildcards is None:
            consumed_wildcards = None
        else:
            if consumed_wildcards is None:
                consumed_wildcards = set()

            if self.wildcard_mapping:
                for wildcard_name, wildcard_value in wildcards.items():
                    if wildcard_name in self.wildcard_mapping:
                        token_name = self.wildcard_mapping[wildcard_name]
                        cur_tokens[token_name] = wildcard_value
                        consumed_wildcards.add(wildcard_name)
                        logger.debug(
                            f"Added token {token_name}:{wildcard_value} "
                            f"from wildcard {wildcard_name} for {self.config_set}"
                        )

        if self.const_mapping:
            for token_name, token_value in self.const_mapping.items():
                cur_tokens[token_name] = token_value
                logger.debug(
                    f"Added token {token_name}:{token_value} " f"for {self.config_set}"
                )

        if log_set is not None and self.overrides and log_set in self.overrides:
            self.overrides[log_set].resolve_tokens(
                log_set, wildcards, cur_tokens, consumed_wildcards
            )  # cur_tokens and consumed_wildcards modified in-place

        return cur_tokens, consumed_wildcards


class Abrije:
    """
    Main class for `abrije`.


    """

    def __init__(self):
        self.parsers: Dict[str, StoredParser] = {}
        """
        Stores all loaded parsers, maps `name1 -> (fullname, type, function)`
        e.g. `'csv_firstrow' -> ('parser_csv_firstrow', 'text', parser_csv_firstrow())`.
        """

        self.log_sets: typing.OrderedDict[str, str] = OrderedDict()
        """
        Stores input patterns to search for log files to process,
        as `log_set_name -> log_set_pattern` with the `log_set_pattern` in 
        snakemake wildcard syntax
        e.g. `'rule_align' -> '{step}/{sample}-{genome}.sam'`.
        """

        self.parser_mapping: Dict[str, str] = {}
        """
        Stores mapping of `log_set -> parser_name` where `parser_name` is
        the name of a parser used for processing the `log_set`.
        """

        self.default_config = AbrijeConfig("defaults")
        """
        Default config for all `log_sets`; parent for all override configs.
        """

        self.all_headings: typing.OrderedDict[str, str] = OrderedDict()
        """
        Used to track heading order.
        Stores a set of all headings in order seen by the algorithm as
        `heading -> heading_type` where `heading_type` is a string later used 
        to reorder headings according to type (e.g. labels first).
        """

        LogRow = Dict[str, str]
        """
        A row in the output stored `heading -> value`.
        """

        self.output_rows: typing.Dict[str, LogRow] = {}
        """
        Stores rows of log data read from `log_set`s as `full_label -> row`; 
        does not need to be ordered as `output_rows` sorted by `full_label` 
        before output generated.
        """

    def add_log_set(self, log_set_name: str, log_set_pattern: str, log_set_type: str):
        """
        Add a `log_set`.

        Args:
            log_set_name: Name of the `log_set`.
            log_set_pattern: Snakemake-style wildcard pattern used to find log
                files to parse for this `log_set`.
            log_set_type: 
        """
        logger.debug(
            f"Adding log_set: "
            f"name {log_set_name}, pattern {log_set_pattern}, type {log_set_type}"
        )
        if log_set_name == "" or log_set_pattern == "" or log_set_type == "":
            raise ValueError("log_set name, pattern and type must not be blank")
        self.log_sets[log_set_name] = log_set_pattern
        self.parser_mapping[log_set_name] = log_set_type

    def add_parser(self, fullname: str, func: ParserFunc) -> None:
        """
        Helper to add a parser to stored parsers, with error and warning
        handling for incompatible types or attempts to replace parsers.
        Only parsers with name starting with the parser prefix 
        `([a-z]*)parser_` are imported, others are silently ignored.
        The prefix before parser determines the parser type. 
        Allowed parser types are `text`, `svtext`, `raw`, and `path` 
        If no type is specified (`parser_`), the default is `text`.
        The text following the prefix gives the parser name. 
        (e.g. `pathparser_test` is a parser named `test` of type `path`).

        Readding a parser of the same name (regardless of type) produces a  
        warning, and the new parser is *not* added.

        Args:
            fullname: The full name (including the parser type prefix) of the
                parser e.g. `pathparser_test`.
            func: The parser function itself.

        Raises:
            ValueError: If `func` is not callable or an invalid parser type 
                specified.
        """
        match = re.match("^([a-z]*)parser_(.*)$", fullname)
        if match:
            parser_type = match.group(1)
            if parser_type == "":
                parser_type = "text"  # default
            parser_name = match.group(2)
            if not callable(func):
                raise ValueError(f"cannot import {fullname} as parser - not callable")
            if not parser_type in ["text", "svtext", "raw", "path"]:
                raise ValueError(
                    f"cannot import {fullname} as parser - unknown type {parser_type}"
                )
            if parser_name in self.parsers:
                warning(
                    f"ignoring parser {fullname} - parser of same name already exists"
                )
                return
            logger.debug(
                f"Adding parser: name {parser_name}"
                f"fullname {fullname}, parser_type {parser_type}, func {func}"
            )
            self.parsers[parser_name] = (fullname, parser_type, func)
        else:
            logger.debug(f"Ignoring (not a parser): {fullname}")

    def import_parsers(
        self,
        import_from: Union[
            ModuleType, Tuple[ParserFunc, ...], List[ParserFunc], Dict[str, ParserFunc]
        ],
    ) -> None:
        """
        Import parsers from a module, `tuple`, `list` or `dict`. 

        A parser is a function that takes parses a log file. 
        Parsers are identified by name.
        The `fullname` of a parser is: `{prefix}parser_{name}`. The `prefix`
        is the type of the parser, while `name` identifies the parser for
        downstream use.

        The types of parser are (given by `prefix`):
        - `text` (default): parameter is open text file handle to parse
        - `svtext`: parameter is open text file with `newline=''`, meant to
          be fed into Python `csv.read()`
        - `raw`: parameter is open binary file handle to parse
        - `path`: parameter is path to a file to parse

        A blank prefix `''` indicates the default parser type.

        A parser function takes (first arg) an open file handle of a text (`text` 
        parser), text with `newline='' (`svtext` ) or binary (`raw`) file 
        (for reading), or a file path string (`path`), (second arg) a dictionary 
        of tokens (potentially containing parse parameters), and returns 
        parallel lists of headings and values as a tuple 
        i.e. `([heading1, heading2, ...], [value1, value2, ...])`.
        
        If `import_from` is a module, all parsers (identified by a valid
        `fullname`) are important from the module.

        If `import_from` is a list or tuple, the `fullname` is obtained from
        the function name itself.

        If `input_from` is a the dict, the `fullname` is the key and the value 
        is the function.

        Args:
            import_from: Module, tuple, list or dict of parsers to import.

        Raises:
            ValueError: If `import_from` as unsupported type, a parser is invalid 
            type or a parser function is not callable.
        """

        if isinstance(import_from, ModuleType):
            logger.debug(f"Adding parsers from module: {import_from.__name__}")
            for name in dir(import_from):
                self.add_parser(name, getattr(import_from, name))
        elif isinstance(import_from, tuple) or isinstance(import_from, list):
            logger.debug(f"Adding parsers from: {import_from}")
            for item in import_from:
                try:
                    name = item.__name__
                except:
                    raise ValueError(
                        f"cannot import {item} as parser - no __name__"
                    ) from None
                self.add_parser(name, item)
        elif isinstance(import_from, dict):
            logger.debug(f"Adding parsers from: {import_from}")
            for name, item in import_from.items():
                self.add_parser(name, item)
        else:
            raise ValueError(f"cannot import from unsupported type {type(import_from)}")

    def add_to_config(
        self, parameters: Dict[str, str], log_set: Optional[str] = None
    ) -> None:
        """
        Adds `parameters` as defaults (if `log_set` is `None` or `"defaults"`) 
        or to the override config for given `log_set`.

        Args:
            parameters: `dict` of `param_name -> param_value`.  Wildcard 
                parameters are specified as `{wildcard_name}` in the 
                `param_name`, all others are considered const parameters.
            log_set: Name of `log_set` if these are for override config of that 
                `log_set`.
        """
        if log_set == "defaults":
            # "defaults" is not a log_set, strip value
            log_set = None

        self.default_config.add_to_config(parameters, log_set)
        # note: no check if log_set actually exists as cannot guarantee log_sets
        # added before config, check_config() does this before processing

    def check_config(self):
        """
        Performs a sanity check to ensure override parameter names match `log_set`s.
        Meant to catch potential errors caused by misspelt `log_set`s/overrides.
        """
        if len(self.log_sets) == 0:
            raise ValueError("no log_sets to process")
        if self.default_config.overrides is None or set(self.log_sets) >= set(
            self.default_config.overrides.keys()
        ):
            pass
        else:
            raise ValueError("some overrides do not match log_set names")

    def resolve_tokens(
        self, log_set: Optional[str], wildcards: Optional[Dict[str, str]]
    ) -> Dict[str, str]:
        """
        Resolve all wildcard or const parameter tokens for a `log_set`.

        Args:
            log_set: Name of the `log_set` to resolve for; used to detect any 
                overrides. May be `None`, in which case no overrides are 
                resolved.

            wildcards: Wildcards as `dict` of `wildcard_name -> wildcard_value` 
                used to resolve any wildcard parameters. May be `None`, in which 
                case only const tokens are resolved.

        Raises:
            RuntimeError: If there were any wildcards not converted to tokens.

        Returns:
            A `dict` of `param_name -> param_value`.
        """
        tokens, consumed_wildcards = self.default_config.resolve_tokens(
            log_set, wildcards
        )
        if wildcards is not None:
            assert (
                consumed_wildcards is not None
            ), "some wildcards consumed when none provided?"
            assert consumed_wildcards <= set(
                wildcards  # this shouldn't occur, can't consume any wildcards not provided
            ), f"consumed unknown wildcards {consumed_wildcards - set(wildcards)}"
            unconsumed_wildcards = set(wildcards) - consumed_wildcards
            if unconsumed_wildcards:
                raise RuntimeError(
                    f"the following wildcards were not converted to tokens: {unconsumed_wildcards}"
                )
            logger.info(f"Resolved tokens for log_set {log_set}: {tokens}")
        else:
            logger.info(f"Resolved universal tokens: {tokens}")
        return tokens

    def process_log_sets(self) -> None:
        """
        Processes all log files given in `log_set`s. Processed output stored in
        object.

        Raises:
            RuntimeError: If this function has already been called.
        """

        self.check_config()

        if self.all_headings:
            raise RuntimeError("second call to process_log_sets() - not supported")

        # logic pseudocode
        # for each log_set_name, log_pattern in self.log_sets:
        #     list files for pattern
        #     for file in file list:
        #         have wildcard values -> get labels, tags, comments
        #             either from wildcards or const, with overrides
        #             logic:
        #                 1) find any const
        #                 2) find any wildcards
        #                 3) if wildcard does not exist, no token
        #         get parser -> process file -> get output dict
        #         make full_label from labels
        #         add comments
        #         tag headings in output
        #         group with any existing full_label, combine headings and data
        # sort full output by full_label
        # write
        logger.info("Processing log sets...")
        # iterate log_sets
        for log_set_name, log_set_pattern in self.log_sets.items():
            parser = self.get_parser(log_set_name)
            logger.debug(
                f"Listing files for log_set {log_set_name} with "
                f"pattern {log_set_pattern}"
            )

            logfile_n = 0
            for logfile_n, (logpath, wildcards_list) in enumerate(
                snakemake.utils.listfiles(log_set_pattern)
            ):
                wildcards = dict(wildcards_list.items())

                logger.debug(
                    f"Processing log file: path {logpath}, wildcards {wildcards}"
                )
                tokens = self.resolve_tokens(log_set_name, wildcards)
                sorted_token_keys = sorted(
                    tokens.keys()
                )  # ensure we sort keys to get same output regardless of parameter order

                def get_tokens_with_prefix(prefix):
                    for key in sorted_token_keys:
                        if key.startswith(prefix):
                            yield (key, tokens[key])

                labels = NamedTokens.new()
                labels.extend(get_tokens_with_prefix("label"))
                comments = NamedTokens.new()
                comments.extend(get_tokens_with_prefix("comment"))
                tags = NamedTokens.new("log_set", log_set_name)
                # log_set is always the first tag
                tags.extend(get_tokens_with_prefix("tag"))

                if len(labels) == 0:
                    logger.info(f"No label tokens found, using path as label")
                    labels.append("labelpath", logpath)

                logger.debug(f"Labels: {labels}")
                logger.debug(f"Comments: {comments}")
                logger.debug(f"Tags: {tags}")

                full_label = ">".join(labels.values)
                logger.debug(f"Full label from is {full_label}")

                log_raw_output = NamedTokens.fromLists(
                    *self.parse_path(parser, logpath, tokens)
                )
                logger.debug(f"Parser output is {log_raw_output}")

                log_output = filter_tokens(log_raw_output, tokens)
                logger.debug(f"Filtered output is {log_raw_output}")

                if len(log_output) == 0:
                    warning("output is empty")

                if log_output.has_redundant_headings():
                    logger.info("Output has redundant headings, making all unique")
                    log_output.make_headings_unique()

                tag_prefix = tags.render_values() + " "
                log_output.tag_headings(tag_prefix)
                comments.tag_headings(tag_prefix)

                logger.debug(f"Tagged comments headings: {comments.headings}")
                logger.debug(f"Tagged headings: {log_output.headings}")

                output_row = self.output_rows.setdefault(full_label, {})

                def add_to_output(heading, value):
                    if heading not in self.all_headings:
                        self.all_headings[heading] = True
                    if heading in output_row and output_row[heading] != value:
                        warning(
                            f"replacing value {heading} for {full_label}, "
                            "add a tag to prevent redundant headings"
                        )
                        # should virtually never happen as log_set, which must be
                        # unique, is used as tag

                    output_row[heading] = value

                def add_all_to_output(named_tokens):
                    for heading, value in named_tokens:
                        add_to_output(heading, value)

                add_to_output("full_label", full_label)
                add_all_to_output(labels)
                add_all_to_output(comments)
                add_all_to_output(log_output)
            logger.info(f"Processed {logfile_n} files for log_set {log_set_name}.")
            if logfile_n == 0:
                warning(f"no log files processed for log_set {log_set_name}")

    # TODO: tests for no parser mapping or parser
    def get_parser(self, log_set_name: str) -> StoredParser:
        """
        Returns stored parser for given `log_set`.

        Args:
            log_set_name: `log_set` to get parser for.

        Raises:
            RuntimeError: If no parser set for the `log_set` or parser could not be 
            found.

        Returns:
            Stored parser for given `log_set`.
        """
        if log_set_name not in self.parser_mapping:
            raise RuntimeError(f"no parser set for log_set {log_set_name}")
        parser_name = self.parser_mapping[log_set_name]
        if parser_name not in self.parsers:
            raise RuntimeError(f"no parser {parser_name} for {log_set_name}")
        parser = self.parsers[parser_name]
        logger.debug(f"Using parser {parser_name} {parser} for log_set {log_set_name}")
        return parser

    # TODO: document open_encoding
    def parse_path(self, parser: StoredParser, path: str, tokens: Dict[str, str]):
        """
        Executes parser function for given path and tokens.

        Args:
            parser: Stored parcel to use.
            path: Log file path to parse.
            tokens: Tokens to pass to parse function (potentially containing 
                parse parameters).

        Returns:
            Output from parser function.
        """
        parser_fullname, parser_type, parser_function = parser
        input_encoding = tokens.get("open_encoding", "utf8")
        if parser_type == "text":
            logger.debug(
                f"'text' parser: Opening text log file {path} with encoding {input_encoding}"
            )
            with open(path, "r", encoding=input_encoding) as handle:
                output = parser_function(handle, tokens)
        elif parser_type == "svtext":
            logger.debug(
                f"'svtext' parser: Opening text log file {path} with encoding {input_encoding}, "
                f"newline ''"
            )
            with open(path, "r", newline="", encoding=input_encoding) as handle:
                output = parser_function(handle, tokens)
        elif parser_type == "raw":
            logger.debug(f"'raw' parser: Opening binary log file {path}")
            with open(path, "rb") as handle:
                output = parser_function(handle, tokens)
        elif parser_type == "path":
            logger.debug(f"'path' parser: Providing path {path} to parser")
            output = parser_function(path, tokens)
        else:
            raise AssertionError(f"unexpected parser_type {parser_type}")
        return output

    # TODO: Ensure we write lables first, and in order?
    def write_output(self, outfile: Union[IO[str], str]) -> None:
        """
        Write output to a open file handle or path.

        Args:
            outfile: An open file handle or path string.

        Raises:
            RuntimeError: If called before processing complete.
        """
        if not self.all_headings:
            raise RuntimeError("write_output() called before process_log_sets()")

        tokens = self.resolve_tokens(None, None)

        output_encoding = tokens.get("output_encoding", "utf8")
        output_navalue = tokens.get("output_navalue", "")
        output_delimiter = tokens.get("output_delimiter", "\t")

        if isinstance(outfile, str):
            csv_file = open(outfile, "w", newline="", encoding=output_encoding)
            logger.info(
                f"Opening output file {outfile} with encoding {output_encoding}"
            )
        else:
            csv_file = outfile

        csv_writer = csv.DictWriter(
            csv_file,
            restval=output_navalue,
            delimiter=output_delimiter,
            fieldnames=self.all_headings,
        )

        logger.debug(
            f"Output delimiter {output_delimiter!r}, NA value {output_navalue!r}"
        )

        logger.debug(f"Writing header, total {len(self.all_headings)} columns")
        csv_writer.writeheader()
        for full_label in sorted(self.output_rows.keys()):
            row = self.output_rows[full_label]
            logger.debug(f"Writing row {full_label}, total {len(row)} valid values")
            csv_writer.writerow(row)

        if csv_file is not outfile:
            csv_file.close()


# TODO move test to unit test
def test():
    abrije_ = Abrije()
    abrije_.import_parsers(abrije.parsers)
    abrije_.add_log_set(
        "step0",
        "logs/0_subsampled_data/{sample_name}___{inputid}_{end_label}.fastq.stats",
        "tsv_wide",
    )

    abrije_.add_log_set(
        "step1",
        "logs/1_trimmed/{sample_name}___{inputid}_{end_label}.fastq.stats",
        "tsv_wide",
    )
    abrije_.add_to_config(
        {
            "{sample_name}": "label1_sample_name",
            "{end_label}": "label3_end_label",
            "{inputid}": "label2_inputid",
            "open_encoding": "utf8",
            "tag2_best": "bag1",
            # "output_delimiter": ",",
        },
    )
    abrije_.add_to_config(
        {"tag1_test": "tag1", "comment1_det": "234"}, log_set="step0",
    )
    abrije_.process_log_sets()
    abrije_.write_output("test.tsv")

    import shlex

    config = {
        "log_set": [
            (
                "step1",
                "logs/1_trimmed/{sample_name}___{inputid}_{end_label}.fastq.stats",
                "tsv_wide",  # allow optional dict as config
            ),
            (
                "step1",
                "logs/1_trimmed/{sample_name}___{inputid}_{end_label}.fastq.stats",
                "tsv_wide",
            ),
        ],  # allow top level defaults dict
        "config": {
            "defaults": {
                "{sample_name}": "label1_sample_name",
                "{end_label}": "label3_end_label",
                "{inputid}": "label2_inputid",
                "open_encoding": "utf8",
                "tag2_best": "bag1",
            },
            "step0": {"tag1_test": "tag1", "comment1_det": "234"},
        },
    }

    # print(shlex.quote(json.dumps(config)))
    # parse cmd line with csv excel for rudimentary quoting, additional quoting use --json


def add_log_set_to_namespace(namespace, log_set: Tuple[str]) -> None:
    """
    Helper to add `log_set` to `argparse` `namespace`.

    Args:
        namespace: `argparse` `namespace` to add `log_set` to.
        log_set: `log_set` to add as tuple of `(name, pattern, type)`.
    """
    logsets = getattr(namespace, "logset", None)
    if logsets is None:
        logsets = []
    logsets.append(log_set)
    setattr(namespace, "logset", logsets)


def add_config_to_namespace(
    namespace, key: str, value: str, log_set_name: str = "defaults"
) -> None:
    """
    Helper to add config keys and values to `argparse` `namespace`.

    Args:
        namespace: `argparse` `namespace` to add config keys and values to.
        key: Config key to add.
        value: Config value to add.
        log_set_name: Name of `log_set` this is config for.
    """
    config = getattr(namespace, "config", None)
    if config is None:
        config = {}
    logset_config = config.setdefault(log_set_name, {})
    logset_config[key] = value
    setattr(namespace, "config", config)


def parse_config_key_values(
    config_params: List[str], namespace, log_set: Optional[str] = None
) -> None:
    """
    Parses key:value pairs for config command-line arguments.

    Args:
        config_params: List of strings as `key:value` or `key=value` to parse. 
            First `:` or `=` used to split key and value.
        namespace: `argparse` namespace to add arguments to (added as 
            `{config_name:{key1:value1...}}`.
        log_set: Name of `log_set` that this is of override config for. If `None`,
            assumed to be `defaults` config and any `config_param` without a
            `:` or `=` will set new `log_set` name for subsequent `config_params`.
            e.g. `log_set=None` and `config_params="k1:v1,k2:v2,step1,k3:v3"`
            will set `{"defaults": {"k1":"v1", "k2":"v2"}, "step1": {"k3":"v3"}}`.
            If `log_set` is not `None`, all `config_params` must be for given 
            `log_set` i.e. all `config_params` must be key:value pairs and 
            contain a `:` or `=`.

    Raises:
        ValueError: If `config_params` are of incorrect format.
    """
    if log_set is None:
        log_set = "defaults"
        new_logset_allowed = True
    else:
        new_logset_allowed = False
    for config_param in config_params:
        if not re.search("[=:]", config_param):
            if new_logset_allowed:
                log_set = config_param
                continue
            else:
                raise ValueError(
                    f"config param '{config_param}' should be 'key=value' or 'key:value'"
                )
        key, value = re.split("[=:]", config_param, 1)
        # print(f"{key} : {value}")
        add_config_to_namespace(namespace, key, value, log_set)


# format:
class ParseLogset(argparse.Action):
    """
    `argparse.Action` to parse `--logset` arguments in CSV format:
    `name,pattern,type(,config...)`, config is `key=value` or `key:value` with 
    first `=` or `:` used as split char.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        splitter = csv.reader(values, delimiter=",")
        for i, row in enumerate(splitter):
            if len(row) < 3:
                parser.error(
                    f'"{values[i]}": '
                    f"{self.dest} must be at least 3 comma-separated values"
                )
            add_log_set_to_namespace(namespace, tuple(row[:3]))
            log_set_name = row[0]
            config_params = row[3:]
            try:
                parse_config_key_values(config_params, namespace, log_set_name)
            except ValueError as e:
                parser.error(f'"{values[i]}": ' + str(e))


#
class ParseConfig(argparse.Action):
    """
    `argparse.Action` to parse `--config` arguments in CSV format:
    `log_set1,key1=value1,key2=value2,log_set2,...`
    """

    def __call__(self, parser, namespace, values, option_string=None):
        splitter = csv.reader(values, delimiter=",")
        for i, row in enumerate(splitter):
            config_params = row
            try:
                parse_config_key_values(config_params, namespace)
            except ValueError as e:
                parser.error(f'"{values[i]}": ' + str(e))


class ParseJSONConfig(argparse.Action):
    """
    `argparse.Action` to parse full config in JSON format. The following
    formats (in pseudo-JSON), or a mixture of the two, are allowed:

    ```
    {
        "log_set": [ # any key that starts with "log_set" or "logset"
            [
                name,
                pattern,
                type 
            ],
            ...
        ],
        "config": { # any key that starts with "config"
            "defaults": {
                key: value,
                ...
            },
            name: { # optional override config for log_set by name 
                key: value,
                ...
            },
        },
    
    }
    ```
    or
    ```
    {
        "log_set": [ # any key that starts with "log_set" or "logset"
            [
                name,
                pattern,
                type,
                { # allow optional 4th element as override config
                    key: value,
                    ...
                }  
            ],
            ...
        ],
        "defaults": { # top-level defaults config dict
            key: value,
            ...
        },
        
    }
    ```
    """

    def __call__(self, parser, namespace, values, option_string=None):
        if not isinstance(values, list):
            values = [values]  # values is not list if no nargs

        for value in values:

            def process_config_dict(log_set_name, config):
                # helper to process a named config dict
                if not isinstance(config, dict):
                    parser.error(
                        f'"{value}": expected {log_set_name} config "{config}" to be a dict/json object'
                    )
                for config_key, config_value in config.items():
                    add_config_to_namespace(
                        namespace, config_key, config_value, log_set_name,
                    )

            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                parser.error(f'"{value}": expected top-level to be a dict/json object')
            for top_key, top_value in parsed.items():
                if top_key.startswith("log_set") or top_key.startswith("logset"):
                    if not isinstance(top_value, list):
                        parser.error(
                            f'"{value}": expected {top_key} to be a list/json array'
                        )
                    for log_set in top_value:
                        if not isinstance(log_set, list):
                            parser.error(
                                f'"{value}": expected log_set "{log_set}" to be a list/json array'
                            )
                        if len(log_set) < 3:
                            parser.error(
                                f'"{value}": expected log_set "{log_set}" to be at least 3 values'
                            )
                        if any(not isinstance(log_set[i], str) for i in range(3)):
                            parser.error(
                                f'"{value}": expected log_set "{log_set}" to be name,pattern,type strings'
                            )
                        add_log_set_to_namespace(namespace, tuple(log_set[:3]))
                        if len(log_set) > 3:  # allow optional dict as config
                            config = log_set[3]
                            log_set_name = log_set[0]
                            process_config_dict(log_set_name, config)

                            if len(log_set) > 4:
                                warning(
                                    f'"{value}": ignoring additional elements in {log_set_name} "{log_set[4:]}"'
                                )
                elif top_key.startswith("config"):
                    if not isinstance(top_value, dict):
                        parser.error(
                            f'"{value}": expected {top_key} to point to a dict/json object'
                        )
                    for config_name, config_dict in top_value.items():
                        process_config_dict(config_name, config_dict)
                elif top_key.startswith("default"):
                    # allow top level defaults dict
                    process_config_dict("defaults", top_value)
                else:
                    parser.error(f'"{value}": unexpected top-level key {top_key}')


def process_arguments(argv):
    parser = argparse.ArgumentParser(
        prog=_PROGRAM_NAME,
        description="abrije is a generic log parser and summariser.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="{} {}".format(_PROGRAM_NAME, _PROGRAM_VERSION),
    )
    parser.add_argument(
        "-v", "--verbose", action="count", help="increase verbosity (v=info, vv=debug)"
    )

    parser.add_argument(
        "-l",
        "--logset",
        action=ParseLogset,
        nargs="+",
        help="Each LOGSET as comma-separated values, Excel-style quoting allowed: "
        '"name,pattern,type(,key1=value1,...)" '
        'with "name" as log_set name, "pattern" as a snakemake-style path pattern '
        '(containing {wildcards}) to find log files to parse, and "type" '
        "specifying the parser to use for the log files. Any additional values "
        "are used as override config for this log_set (key and value pairs "
        "separated by : or =).",
    )

    parser.add_argument(
        "-c",
        "--config",
        action=ParseConfig,
        nargs="+",
        help="Config as comma-separated values, Excel-style quoting allowed. "
        'e.g. "key1=value1,key2=value2,log_set1,key3=value3" '
        'with "key1=value1" and "key2=value2" used for defaults. and '
        '"key3=value3" used for "log_set1" overrides. Key and value can be '
        "separated by : or =, first one found used.",
    )

    parser.add_argument(
        "-j",
        "--json",
        nargs="+",
        action=ParseJSONConfig,
        help="Full config as json e.g. "
        '\'{"log_set": [name1,pattern1,type1],...], '
        '"config": {"defaults": {key1:value1,...}, name1: {key2:value2,...}}}\''
        ". Note that quotes must be escaped as appropriate for command line. "
        "Can be used instead of, or in addition to, --logset and --config.",
    )

    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="output filename, will be replaced if exists; stdout if not given",
    )
    # TODO: parser import

    args = parser.parse_args(argv)
    set_verbosity(args.verbose)
    logger.info(f"Verbosity: {args.verbose}")
    logger.info(f"List of log_sets: {args.logset}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Output file: {args.output}")
    return args


def execute_abrije(argv=None, return_result=False):
    # return_result = False will print output to stdout if no output file set
    # return_result = True will return output to caller instead
    if argv is None:
        argv = sys.argv[1:]  # if parameters not provided, use sys.argv
    args = process_arguments(argv)

    abrije_ = Abrije()
    abrije_.import_parsers(abrije.parsers)
    if args.logset:
        for log_set in args.logset:
            abrije_.add_log_set(*log_set)

    if args.config:
        for config_name, parameters in args.config.items():
            abrije_.add_to_config(parameters, config_name)

    abrije_.process_log_sets()
    if args.output is not None:
        abrije_.write_output(args.output)
    else:
        with io.StringIO() as out_buffer:
            abrije_.write_output(out_buffer)
            output = out_buffer.getvalue()
        if return_result:
            return output
        print(output)





if __name__ == "__main__":
    # main()
    # sys.path.append(".") # cheat for importing unpackaged abrije
    # import doctest

    # doctest.testmod(optionflags = doctest.ELLIPSIS)
    # doctest.testmod()
    execute_abrije()
