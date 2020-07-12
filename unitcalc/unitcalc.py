#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=C0111     # docstrings are always outdated and wrong
# pylint: disable=W0511     # todo is encouraged
# pylint: disable=R0902     # too many instance attributes
# pylint: disable=C0302     # too many lines in module
# pylint: disable=C0103     # single letter var names
# pylint: disable=R0911     # too many return statements
# pylint: disable=R0912     # too many branches
# pylint: disable=R0915     # too many statements
# pylint: disable=R0913     # too many arguments
# pylint: disable=R1702     # too many nested blocks
# pylint: disable=R0914     # too many local variables
# pylint: disable=R0903     # too few public methods
# pylint: disable=E1101     # no member for base
# pylint: disable=W0201     # attribute defined outside __init__

import re
import sys
from icecream import ic
import click
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from Levenshtein import StringMatcher


def eprint(*args, **kwargs):
    kwargs.pop('file', None)
    print(*args, **kwargs, file=sys.stderr)


def find_unit(*, ulist, in_unit, verbose=False):
    distance = -1
    for unit in ulist:
        dist = StringMatcher.distance(in_unit, unit)
        if distance < 0:
            distance = dist
            winning_unit = unit
        else:
            if dist < distance:
                distance = dist
                winning_unit = unit
    if verbose:
        eprint("Converting {0} to {1}".format(in_unit, winning_unit))

    return winning_unit


def topint(*, fromq, ureg, verbose=False):

    if not fromq[0].isdigit():
        assert fromq[0] == '.'
        fromq = '0' + fromq

    # find the end of the magnitude
    for index, letter in enumerate(fromq):
        if letter.isalpha():  # ",".isalpha() == False (and .)
            if letter == 'e':
                if not fromq[index + 1].isdigit():
                    break
            else:
                break

    if verbose:
        ic(fromq)

    #ic(fromq)
    #ic(index)
    if index:
        magnitude = fromq[:index].replace(',', '')
        #ic(magnitude)
        try:
            magnitude = float(magnitude)
        except ValueError:
            # should use https://github.com/sopel-irc/sopel/blob/master/sopel/tools/calculation.py
            # or sage
            expression_pattern = re.compile("[0-9/\*e.+\-()]")
            for item in magnitude:
                assert expression_pattern.match(item)

            if verbose:
                ic(magnitude)

            magnitude = float(eval(magnitude))

            #assert '/' in magnitude
            #num, denom = magnitude.split('/')
            #num = float(num)
            #denom = float(denom)
            #magnitude = float(num / denom)
    else:
        magnitude = fromq
    unit = fromq[index:]

    if verbose:
        ic(magnitude)
        ic(unit)

    try:
        fromq_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        if verbose:
            ic(e)
        found_unit = find_unit(ulist=dir(ureg), in_unit=unit, verbose=verbose)
        if verbose:
            ic(found_unit)
        fromq_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    fromq_parsed = Q_(magnitude, fromq_target)

    if verbose:
        ic(fromq_parsed)

    return fromq_parsed


@click.command()
@click.argument('fromq', required=True)
@click.argument('toq', required=True)
@click.option('--verbose', is_flag=True)
def cli(fromq, toq, verbose):

    ureg = UnitRegistry(system='mks')
    assert not toq[0].isdigit()

    fromq_parsed = topint(fromq, ureg, verbose=verbose)

    if verbose:
        #ic(fromq)
        ic(toq)

    try:
        toq_target = ureg.parse_units(toq)
    except UndefinedUnitError as e:
        if verbose:
            ic("UndefinedUnitError:", e)

        found_unit = find_unit(dir(ureg), toq, verbose)
        toq_target = ureg.parse_units(found_unit)

    if verbose:
        ic(toq_target)

    fromq_converted = fromq_parsed.to(toq_target)
    if verbose:
        ic(int(fromq_converted))
        ic(fromq_converted.magnitude)

    print(fromq_converted)


if __name__ == '__main__':
    cli()
