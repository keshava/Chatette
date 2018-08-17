#!/usr/bin/env python3

from enum import Enum
import re

from utils import *

COMMENT_SYM = ';'
ESCAPE_SYM = '\\'

ALIAS_SYM = '~'
SLOT_SYM = '@'
INTENT_SYM = '%'
UNIT_OPEN_SYM = '['
UNIT_CLOSE_SYM = ']'

VARIATION_SYM = '#'
RAND_GEN_SYM = '?'
PERCENT_GEN_SYM = '/'
CASE_GEN_SYM = '&'

ALT_SLOT_VALUE_NAME_SYM = '='

INCLUDE_FILE_SYM = '|'

RESERVED_VARIATION_NAMES = ["all-variations-aggregation", "rules", "nb-gen-asked"]

# This regex finds patterns like this `[name#variation?randgen/percentgen]`
# with `variation`, `randgen` and `percentgen` optional
# TODO make this reflect the state of the symbols defined before
pattern_modifiers = re.compile(r"\[(?P<casegen>&)?(?P<name>[^#\[\]\?]*)(?:#(?P<variation>[^#\[\]\?]*))?(?:\?(?P<randgen>[^#\[\]\?/]*)(?:/(?P<percentgen>[^#\[\]\?]*))?)?\]")
pattern_nb_gen_asked = re.compile(r"\]\((?P<nbgen>[0-9]+)\)")
pattern_comment = re.compile(r"(?<!\\);")


class Unit(Enum):
    word = 1  # simple word, no other info needed
    word_group = 2  # word group with modifiers
    alias = 3  # alias with modifiers
    slot = 4  # slot with modifiers
    intent = 5  # intent with modifiers and generation number

class LineType(Enum):
    empty = 1
    comment = 2
    alias_declaration = 3
    slot_declaration = 4
    intent_declaration = 5
    include_file = 6


def strip_comments(text):
    match = pattern_comment.search(text)
    if match is None:
        return text
    return text[:match.start()].rstrip()

def is_start_unit_sym(char):
    return (char == UNIT_OPEN_SYM or char == ALIAS_SYM or \
            char == SLOT_SYM or char == INTENT_SYM)
def is_unit_start(text):
    return (len(text) > 0 and is_start_unit_sym(text[0]))

def get_unit_type(unit):
    if unit.startswith(UNIT_OPEN_SYM):
        return Unit.word_group
    elif unit.startswith(ALIAS_SYM):
        return Unit.alias
    elif unit.startswith(SLOT_SYM):
        return Unit.slot
    elif unit.startswith(INTENT_SYM):
        return Unit.intent
    else:
        raise RuntimeError("Internal error: tried to get the unit type of "+
            "something that was not a unit")


def find_nb_gen_asked(intent):
    """
    Finds the number of generation asked for the provided intent string and
    returns it (or `None` if it wasn't provided).
    """
    nb_gen_asked = None
    one_found = False
    for match in pattern_nb_gen_asked.finditer(intent):
        start_index = match.start()
        if one_found:
            raise SyntaxError("Expected only one number of generation asked in "+
                intent)
        else:
            one_found = True
        match = match.groupdict()

        nb_gen_asked = match["nbgen"]
    return nb_gen_asked


def get_all_rules_in_variations(definition):
    """
    Returns a list of all the rules for all variations of `definition`
    which is a definition for an alias or a slot (nothing else).
    """
    # `definition` is a dict indexed by the names of the variation, each
    # containing a list of rules
    all_rules = []
    for variation in definition:
        all_rules.extend(definition[variation])
    return all_rules

def get_all_rules_in_intent_variations(definition):
    """As `get_all_rules_in_variations` for intents"""
    # `definition` is a dict indexed by the names of the variation, each
    # containing a dict with the nb of generations to do for this intent
    # and the rules in `rules`
    all_rules = []
    for variation in definition:
        all_rules.extend(definition[variation]["rules"])
    return all_rules