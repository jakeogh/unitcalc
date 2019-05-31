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
    eprint("Converting {0} to {1}".format(in_unit, winning_unit))
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

    if verbose:
        eprint("from:", fromq)
        eprint("to:", toq)

    magnitude = float(fromq[:index])
    unit = fromq[index:]
    if verbose:
        eprint("from magnitude:", magnitude)
        eprint("from unit:", unit)

    try:
        fromq_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        eprint("UndefinedUnitError:", e)
        found_unit = find_unit(dir(ureg), unit)
        fromq_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    fromq_parsed = Q_(magnitude, fromq_target)
    #try:
    #    fromq_parsed = magnitude * fromq_target
    #except pint.errors.OffsetUnitCalculusError:



    try:
        toq_target = ureg.parse_units(toq)
    except UndefinedUnitError as e:
        eprint("UndefinedUnitError:", e)
        found_unit = find_unit(dir(ureg), toq)
        toq_target = ureg.parse_units(found_unit)

    fromq_converted = fromq_parsed.to(toq_target)


    if verbose:
        eprint("to unit:", toq)

    print(fromq_converted)


if __name__ == '__main__':
    unitcalc()
