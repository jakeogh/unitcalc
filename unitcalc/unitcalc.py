#!/usr/bin/env python3
# -*- coding: utf8 -*-

from icecream import ic
import click
from pint import UnitRegistry
from pint.errors import UndefinedUnitError
from kcl.printops import eprint
from Levenshtein import StringMatcher

ureg = UnitRegistry()
Q_ = ureg.Quantity


def find_unit(ulist, in_unit, verbose):
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
    if verbose: eprint("Converting {0} to {1}".format(in_unit, winning_unit))
    return winning_unit


def topint(fromq, verbose=False):
    assert fromq[0].isdigit()
    for index, letter in enumerate(fromq):
        if letter.isalpha():  # ",".isalpha() == False (and .)
            break

    if verbose:
        ic(fromq)

    magnitude = fromq[:index].replace(',', '')
    magnitude = float(magnitude)
    unit = fromq[index:]

    if verbose:
        ic(magnitude)
        ic(unit)

    try:
        fromq_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        if verbose: ic("UndefinedUnitError:", e)
        found_unit = find_unit(dir(ureg), unit, verbose)
        fromq_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    fromq_parsed = Q_(magnitude, fromq_target)

    if verbose:
        ic(fromq_parsed)

    return fromq_parsed



#@click.group()
#def cli():
#    pass
#
#
#@cli.command()
#@click.option('--verbose', is_flag=True)
#def shell(verbose):
#    ic(dir(ureg))
#    import IPython
#    IPython.embed()


@click.command()
@click.argument('fromq', required=False)
@click.argument('toq', required=False)
@click.option('--shell', is_flag=True)
@click.option('--verbose', is_flag=True)
def cli(fromq, toq, shell, verbose):

    #assert fromq[0].isdigit()
    assert not toq[0].isdigit()
    #for index, letter in enumerate(fromq):
    #    if letter.isalpha():  # ",".isalpha() == False (and .)
    #        break

    fromq_parsed = topint(fromq, verbose=verbose)

    #ic()
    if verbose:
        #ic(fromq)
        ic(toq)

    #magnitude = fromq[:index].replace(',', '')
    #magnitude = float(magnitude)
    #unit = fromq[index:]

    #if verbose:
    #    ic(magnitude)
    #    ic(unit)

    #try:
    #    fromq_target = ureg.parse_units(unit)
    #except UndefinedUnitError as e:
    #    if verbose: ic("UndefinedUnitError:", e)
    #    found_unit = find_unit(dir(ureg), unit, verbose)
    #    fromq_target = ureg.parse_units(found_unit)

    #Q_ = ureg.Quantity
    #fromq_parsed = Q_(magnitude, fromq_target)

    #if verbose:
    #    ic(fromq_parsed)

    try:
        toq_target = ureg.parse_units(toq)
    except UndefinedUnitError as e:
        if verbose: ic("UndefinedUnitError:", e)
        found_unit = find_unit(dir(ureg), toq, verbose)
        toq_target = ureg.parse_units(found_unit)

    if verbose:
        ic(toq_target)

    fromq_converted = fromq_parsed.to(toq_target)
    print(fromq_converted)


if __name__ == '__main__':
    cli()
