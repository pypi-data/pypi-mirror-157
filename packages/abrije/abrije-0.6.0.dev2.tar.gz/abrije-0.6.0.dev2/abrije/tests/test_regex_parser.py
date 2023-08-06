#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abrije.parsers import *
import pprint

dedup_params = {
"parse_ignorecase" : "True",
"parse_unicode" : "True",
"parse_regex_reads1" : "[0-9\\-:, ]+ INFO Reads: .*(?P<heading>Input Reads): (?P<value>[0-9.]+)",
"parse_regex_reads2" : "[0-9\\-:, ]+ INFO Reads: .*(?P<heading>Read Pairs): (?P<value>[0-9.]+)",
"parse_regex_reads3" : "[0-9\\-:, ]+ INFO (?P<heading>.*reads.*out[^\\:]*): (?P<value>[0-9.]+)",
"parse_regex_position" : "[0-9\\-:, ]+ INFO (?P<heading>.+number.+position[^\\:]*): (?P<value>[0-9.]+)"
}

dedup_expected = (['Input Reads',
  'Read pairs',
  'Number of reads out',
  'Total number of positions deduplicated',
  'Mean number of unique UMIs per position',
  'Max. number of unique UMIs per position'],
 ['7318900', '7318900', '4270144', '3809138', '1.12', '235'])

dedup_input = "abrije/tests/dedup_example.log"

dedup_params1 = {
"heading_prefix" : "hpr_", # test adding prefix to heading (all)
"heading_suffix" : "_hsf", # test adding suffix to heading (all)
"value_prefix" : "vpr_", # test adding prefix to value (all)
"value_suffix" : "_vsf", # test adding suffix to value (all)
"parse_ignorecase" : "True",
"parse_unicode" : "True",
"parse_regex_reads1" : "[0-9\\-:, ]+ INFO Reads: .*(?P<heading1>Input Reads)(?P<heading2__rsf>): (?P<value1>[0-9.]+)(?P<value2__rsf>)",
    # above adds _rsf as suffix to heading and value
"parse_regex_reads2" : "[0-9\\-:, ]+ INFO Reads: .*(?P<heading1>Read Pairs)(?P<heading0_rpr_>): (?P<value1>[0-9.]+)(?P<value0_rpr_>)",
    # above adds rpr_ as prefix to heading and value
"parse_regex_reads3" : "[0-9\\-:, ]+ INFO (?P<heading1>.*reads.*out[^\\:]*): (?P<heading2>(?P<value>[0-9.]+))",
    # above appends value as suffix to heading
"parse_regex_position" : "[0-9\\-:, ]+ INFO (?P<heading>.+number.+position[^\\:]*): (?P<value0>(?P<value1>[0-9.]+))"
    # above appends value twice back to back
}

dedup_expected1 = (['hpr_Input Reads_rsf_hsf',
  'hpr_rpr_Read pairs_hsf',
  'hpr_Number of reads out4270144_hsf',
  'hpr_Total number of positions deduplicated_hsf',
  'hpr_Mean number of unique UMIs per position_hsf',
  'hpr_Max. number of unique UMIs per position_hsf'],
 ['vpr_7318900_rsf_vsf', 'vpr_rpr_7318900_vsf', 'vpr_4270144_vsf', 'vpr_38091383809138_vsf', 'vpr_1.121.12_vsf', 'vpr_235235_vsf'])

dedup_input1 = "abrije/tests/dedup_example.log"


rsem_params = {
    "parse_multiline" : "True",
    "parse_regex_N0_number_of_unalignable_reads" :
        "^([0-9.]+) [0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+\n",
    "parse_regex_N1_number_of_alignable_reads" :
        "^[0-9.]+ ([0-9.]+) [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+\n",
    "parse_regex_N2_number_of_filtered_reads" :
        "^[0-9.]+ [0-9.]+ ([0-9.]+) [0-9.]+\n[0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+\n",
    "parse_regex_N_tot_total_number_of_reads" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ ([0-9.]+)\n[0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+\n",

    "parse_regex_nUnique_number_of_reads_aligned_uniquely_to_a_gene" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+\n([0-9.]+) [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+\n",
    "parse_regex_nMulti_number_of_reads_aligned_to_multiple_genes" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ ([0-9.]+) [0-9.]+\n[0-9.]+ [0-9.]+\n",
    "parse_regex_nUncertain_number_of_reads_aligned_to_multiple_locations" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+ ([0-9.]+)\n[0-9.]+ [0-9.]+\n",

    "parse_regex_nHits_number_of_total_alignments" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+ [0-9.]+\n([0-9.]+) [0-9.]+\n",
    "parse_regex_read_type" :
        "^[0-9.]+ [0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ [0-9.]+ [0-9.]+\n[0-9.]+ ([0-9.]+)\n",
}

rsem_expected = (['N0_number_of_unalignable_reads',
  'N1_number_of_alignable_reads',
  'N2_number_of_filtered_reads',
  'N_tot_total_number_of_reads',
  'nUnique_number_of_reads_aligned_uniquely_to_a_gene',
  'nMulti_number_of_reads_aligned_to_multiple_genes',
  'nUncertain_number_of_reads_aligned_to_multiple_locations',
  'nHits_number_of_total_alignments',
  'read_type'],
 ['429826',
  '18765323',
  '0',
  '19195149',
  '17610329',
  '1154994',
  '14360103',
  '93404229',
  '3'])

rsem_input = "abrije/tests/rsem_example.cnt"

def test_regex_parser_dedup():
    with open(dedup_input) as inputfile:
        res = textparser_regex(inputfile, dedup_params)
        pprint.pprint(res) # print for updating expected, if needed
        assert res==dedup_expected

    with open(dedup_input1) as inputfile:
        res = textparser_regex(inputfile, dedup_params1)
        pprint.pprint(res) # print for updating expected, if needed
        assert res==dedup_expected1


def test_regex_parser_rsem():
    with open(rsem_input) as inputfile:
        res = textparser_regex(inputfile, rsem_params)
        pprint.pprint(res)
        assert res==rsem_expected

# for printing expected
def main():
    test_regex_parser_dedup()
    test_regex_parser_rsem()

if __name__ == '__main__':
    main()