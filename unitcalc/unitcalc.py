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
from typing import List

import click
from enumerate_input import enumerate_input
from Levenshtein import StringMatcher
from number_parser import parse as parse_words_to_numbers
from pint import UnitRegistry
from pint.errors import UndefinedUnitError


class UnitAlreadyDefinedError(ValueError):
    pass


def eprint(*args, **kwargs):
    kwargs.pop('file', None)
    print(*args, **kwargs, file=sys.stderr)


try:
    from icecream import ic
except ImportError:
    ic = eprint


def human_filesize_to_int(size,
                          verbose: bool = False,
                          debug: bool = False
                          ):
    u = UnitRegistry()
    i = u.parse_expression(size)
    result = i.to('bytes').magnitude
    #result = int(result)
    if verbose:
        ic(result)
    #assert isinstance(result, int)
    return int(result)


def add_unit_to_ureg(ureg, *,
                     unit_name: str,
                     unit_def: str,
                     unit_symbol: str,
                     unit_aliases: List[str],
                     verbose: bool,
                     debug: bool,):
    if verbose:
        ic(unit_name, unit_def, unit_symbol, unit_aliases)

    assert unit_name not in unit_aliases
    assert unit_symbol not in unit_aliases

    if unit_name in ureg:
        raise UnitAlreadyDefinedError(unit_name)

    unit_def_string = '{unit_name} = {unit_def} = {unit_symbol} = '
    unit_def_string = unit_def_string.format(unit_name=unit_name,
                                             unit_def=unit_def,
                                             unit_symbol=unit_symbol,)
    if unit_aliases:
        unit_def_string += '= '.join(unit_aliases)

    if verbose:
        ic(unit_def_string)

    ureg.define(unit_def_string)
    return ureg


def construct_unitregistry(verbose: bool,
                           debug: bool,):
    ureg = UnitRegistry(system='mks')
    ureg.enable_contexts("Gaussian")  # https://github.com/hgrecco/pint/issues/1205

    # https://en.wikipedia.org/wiki/Ell
    ureg = add_unit_to_ureg(ureg,
                            unit_name='ell',
                            unit_def='45 * inch',
                            unit_symbol='_',
                            unit_aliases=[],
                            verbose=verbose,
                            debug=debug,)
    ureg = add_unit_to_ureg(ureg,
                            unit_name='scottish_ell',
                            unit_def='37 * inch',
                            unit_symbol='_',
                            unit_aliases=[],
                            verbose=verbose,
                            debug=debug,)

    # https://en.wikipedia.org/wiki/Ancient_Egyptian_units_of_measurement
    # https://www.youtube.com/watch?v=jyFkBaKARAs
    # pi/6
    ureg = add_unit_to_ureg(ureg,
                            unit_name='royal_cubit',
                            unit_def='52.3 * cm',
                            unit_symbol='_',
                            unit_aliases=[],
                            verbose=verbose,
                            debug=debug,)

    return ureg


def find_unit(*,
              ulist,
              in_unit,
              verbose: bool,
              debug: bool,
              ):

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
    eprint("Warning: converting {0} to {1}".format(in_unit, winning_unit))
    return winning_unit




def convert_atom_to_pint(*,
                         fromq,
                         ureg,
                         verbose: bool,
                         debug: bool,
                         ):

    if verbose or debug:
        ic(fromq)

    # this might need to be earlier
    if not fromq[0].isdigit():
        if fromq[0] == '.':
            fromq = '0' + fromq

    # find the end of the magnitude
    index = None
    for index, letter in enumerate(fromq):
        if letter.isalpha():  # ",".isalpha() == False (and .)
            if letter == 'e':
                if not fromq[index + 1].isdigit():
                    break
            else:
                break

    if verbose:
        ic(fromq)

    if index:
        magnitude = fromq[:index].replace(',', '')
        try:
            magnitude = float(magnitude)
        except ValueError:
            # should use https://github.com/sopel-irc/sopel/blob/master/sopel/tools/calculation.py
            # or sage
            expression_pattern = re.compile(r"[0-9/\*e.+\-()]")
            for item in magnitude:
                assert expression_pattern.match(item)

            if verbose:
                ic(magnitude)

            assert magnitude[0].isdigit()
            magnitude = float(eval(magnitude))

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
        found_unit = find_unit(ulist=dir(ureg),
                               in_unit=unit,
                               verbose=verbose,
                               debug=debug,)
        if verbose:
            ic(found_unit)
        fromq_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    fromq_parsed = Q_(magnitude, fromq_target)

    if verbose:
        ic(fromq_parsed)

    return fromq_parsed


# remove duplicat spaces, convert words to numbers
def normalize_human_input(*,
                          human_input: str,
                          verbose: bool,
                          debug: bool,
                          ):
    if verbose or debug:
        ic(human_input)

    # normalize whitespace to single space
    human_input = human_input.split(' ')
    human_input = ' '.join([i for i in human_input if i])

    human_input = parse_words_to_numbers(human_input)

    return human_input


#todo, make sure scientific notation and equations work
def split_human_input_on_numbers(*,
                                 human_input: str,
                                 verbose: bool,
                                 debug: bool,
                                 ):
    if (verbose or debug):
        ic(human_input)

    #list_of_human_input_atoms = re.split(r"\s(?=[0-9]*.)", human_input)
    #list_of_human_input_atoms = re.split(r"\s(?=[0-9]*\.*[0-9]*[ ]*\D)", human_input)
    #list_of_human_input_atoms = re.split(r"[0-9]*\.*[0-9]*[ ]*\D", human_input)
    list_of_human_input_atoms = re.findall(r'\d+[^\d]+', human_input)
    if (verbose or debug):
        ic(list_of_human_input_atoms)
    return list_of_human_input_atoms


# this takes a arb string, which could be many atoms, and yields pint atoms
def generate_pint_atoms_from_string(*,
                                    human_input: str,
                                    ureg,
                                    verbose: bool,
                                    debug: bool,
                                    ):

    human_input = normalize_human_input(human_input=human_input,
                                        verbose=verbose,
                                        debug=debug,)
    if (verbose or debug):
        ic(human_input)

    # at this point, the string is [number] [space] [unit description] so split on numbers

    human_input_atoms = split_human_input_on_numbers(human_input=human_input,
                                                     verbose=verbose,
                                                     debug=debug,)

    #magnitude = 0.0
    #pint_atoms = []
    for atom in human_input_atoms:
        ic(atom)

        pint_atom = convert_atom_to_pint(fromq=atom,
                                         ureg=ureg,
                                         verbose=verbose,
                                         debug=debug,)

        ic(pint_atom)

        #magnitude += pint_atom.magnitude
        #ic(magnitude)
        #pint_atoms.append(pint_atom)
        yield pint_atom


# this is the last step
def convert_pint_atom_to_unit(*,
                              pint_atom,
                              to_unit_string,
                              ureg,
                              verbose: bool,
                              debug: bool,
                              ):

    assert not to_unit_string[0].isdigit()

    if verbose:
        #ic(fromq)
        ic(to_unit_string)

    try:
        to_unit_string_target = ureg.parse_units(to_unit_string)
    except UndefinedUnitError as e:
        if verbose:
            ic("UndefinedUnitError:", e)

        found_unit = find_unit(ulist=dir(ureg),
                               in_unit=to_unit_string,
                               verbose=verbose,
                               debug=debug,)
        to_unit_string_target = ureg.parse_units(found_unit)

    if verbose:
        ic(to_unit_string_target)

    fromq_converted = pint_atom.to(to_unit_string_target)
    if verbose:
        ic(fromq_converted)
        ic(fromq_converted.magnitude)

    return fromq_converted


@click.command()
@click.argument('quantity', required=True)
@click.argument('to_units', nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--debug', is_flag=True)
@click.option('--ipython', is_flag=True)
def cli(quantity: str,
        to_units: str,
        verbose: bool,
        debug: bool,
        ipython: bool,):

    if verbose:
        ic(quantity, to_units)

    ureg = construct_unitregistry(verbose=verbose, debug=debug,)

    #atoms_magnitude = 0.0
    for atom in generate_pint_atoms_from_string(human_input=quantity,
                                                ureg=ureg,
                                                verbose=verbose,
                                                debug=debug,):

        #atom_converted = convert_pint_atom_to_unit(pint_atom=atom,
        #                                           to_unit_string=unit,
        #                                           ureg=ureg,
        #                                           verbose=verbose,
        #                                           debug=debug,)
        ic(atom)

        if not to_units:
            print(atom.to_base_units())
            return

    #for unit in to_units:
    #    fromq_converted = convert_pint_atom_to_unit(fromq_pint=fromq_pint,
    #                                                to_unit_string=unit,
    #                                                ureg=ureg,
    #                                                verbose=verbose,
    #                                                debug=debug,)

    #    print(fromq_converted)

    #if ipython:
    #    import IPython; IPython.embed()
