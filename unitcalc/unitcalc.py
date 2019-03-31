#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import click
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from kcl.printops import eprint

ureg = UnitRegistry()
Q_ = ureg.Quantity

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

    fromq_target = ureg.parse_units(unit)

    try:
        fromq_parsed = magnitude * fromq_target
    except UndefinedUnitError:
        eprint("UndefinedUnitError:")
        for unitname in dir(ureg):
            if unit in unitname:
                print('\t'+unitname)
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
