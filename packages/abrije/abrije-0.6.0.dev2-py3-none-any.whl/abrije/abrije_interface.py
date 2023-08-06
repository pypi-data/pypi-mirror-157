#!/usr/bin/env python
# -*- coding: utf-8 -*
import json
import shlex

snakemake_rules = None

def abrij_init(rules):
    global snakemake_rules
    snakemake_rules = rules

def abrij_log_set(rule_name, optional = False):
    # get rule_name from rules, and prepare as a log_set
    # if optional = True, return None instead of throwing exception in case rule is has no abrije_ params
    global snakemake_rules
    try:
        rule_obj = getattr(snakemake_rules, rule_name)
        rule_params = getattr(rule_obj, "params")
        rule_log = getattr(rule_obj, "log")
    except AttributeError:
        raise Exception(f"abrije: rule {rule_name} does not exist or has no log/params attr")
    
    log_type = None
    rule_valid = False # set to True if any abrije_ param is found
    for param_name in dir(rule_params):
        if param_name.startswith("abrije_"):
            rule_valid = True
            if param_name=="abrije_log_type":
                log_type = getattr(rule_params, param_name)
            else:
                raise Exception(f"abrije: rule {rule_name} has unknown abrije param {param_name}") 

    if not rule_valid:
        if optional:
            return None
        raise Exception(f"abrije: rule {rule_name} has no abrije_ params")
    
    if log_type is None:
        raise Exception(f"abrije: rule {rule_name} has no abrije_log_type")
    if not rule_log or len(rule_log)>1:
        raise Exception(f"abrije: rule {rule_name} should have single log line")
    return (rule_name, rule_log[0], log_type)


def abrij_log_sets(rule_list):
    # process all rules in rule_list as log_sets
    log_sets = []
    for rule_name in rule_list:
        log_sets.append(abrij_log_set(rule_name))
    return log_sets

def _abrij_is_rule(obj):
    # returns True if obj is a snakemake rule
    # return isinstance(obj, snakemake.rules.RuleProxy)
    return hasattr(obj, "params")

def abrij_all_log_sets():
    # find all rules, and attempt to process as log_sets with optional enabled
    # any rules with no abrije_ params will be ignored
    global snakemake_rules
    log_sets = []
    for item in dir(snakemake_rules):
        obj = getattr(snakemake_rules, item)
        if _abrij_is_rule(obj):
            rule_name = item
            log_set = abrij_log_set(rule_name, optional = True)
            if log_set is not None:
                log_sets.append(log_set)
    return log_sets

def abrij_json_param(abrij_config):
    # returns json param to be used when calling abrije
    # returns as a lambda to prevent any wildcard substitution
    return lambda wildcards: shlex.quote(json.dumps(abrij_config))