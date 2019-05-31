#!/usr/bin/env python3
# -*- coding: utf8 -*-

import click
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from kcl.printops import eprint
from Levenshtein import StringMatcher

ureg = UnitRegistry()
Q_ = ureg.Quantity



def find_unit(ulist, in_unit):
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
    return winning_unit



@click.command()
@click.argument('fromq')
@click.argument('toq')
@click.option('--verbose', is_flag=True)
def unitcalc(fromq, toq, verbose):
    assert fromq[0].isdigit()
    assert not toq[0].isdigit()
    for index, letter in enumerate(fromq):
        if letter.isalpha():
            break
    magnitude = float(fromq[:index])
    unit = fromq[index:]
    if verbose:
        eprint("magnitude:", magnitude)
        eprint("unit:", unit)

    try:
        fromq_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        eprint("UndefinedUnitError:", e)
        found_unit = find_unit(dir(ureg), unit)
        fromq_target = ureg.parse_units(found_unit)

    try:
        fromq_parsed = magnitude * fromq_target
    except UndefinedUnitError as e:
        eprint("UndefinedUnitError:", e)
        for unitname in dir(ureg):
            if unit in unitname:
                print('\t' + unitname)
            print("\n\n\n")
            print(dir(ureg))
        quit(1)

    if verbose:
        eprint("toq:", toq)

    toq_parsed = ureg.parse_units(toq)
    fromq_converted = fromq_parsed.to(toq_parsed)

    if verbose:
        eprint("to unit:", toq)

    print(fromq_converted)


if __name__ == '__main__':
    unitcalc()
