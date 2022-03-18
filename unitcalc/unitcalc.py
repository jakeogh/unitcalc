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
from decimal import Decimal
from math import inf
from typing import List
from typing import Optional
from typing import Union

import click
from asserttool import ic
from clicktool import click_add_options
from clicktool import click_global_options
from eprint import eprint
from Levenshtein import StringMatcher
from number_parser import parse_number
from pint import UnitRegistry  # slow import
from pint.errors import UndefinedUnitError


class UnitAlreadyDefinedError(ValueError):
    pass


def get_all_unit_names(ureg):
    all_names = set(dir(ureg))


def human_filesize_to_int(
    size: str,
    *,
    verbose: Union[bool, int, float],
):
    u = UnitRegistry()
    i = u.parse_expression(size)
    result = i.to("bytes").magnitude
    # result = int(result)
    if verbose:
        ic(result)
    # assert isinstance(result, int)
    return int(result)


def add_unit_to_ureg(
    *,
    ureg: UnitRegistry,
    unit_name: str,
    unit_def: str,
    unit_symbol: str,
    unit_aliases: List[str],
    verbose: Union[bool, int, float],
):
    if verbose == inf:
        ic(unit_name, unit_def, unit_symbol, unit_aliases)

    assert unit_name not in unit_aliases
    assert unit_symbol not in unit_aliases

    if unit_name in ureg:
        raise UnitAlreadyDefinedError(unit_name)

    unit_def_string = "{unit_name} = {unit_def} = {unit_symbol} = "
    unit_def_string = unit_def_string.format(
        unit_name=unit_name,
        unit_def=unit_def,
        unit_symbol=unit_symbol,
    )
    if unit_aliases:
        unit_def_string += "= ".join(unit_aliases)

    if verbose == inf:
        ic(unit_def_string)

    ureg.define(unit_def_string)
    return ureg


def construct_unitregistry(
    *,
    verbose: Union[bool, int, float],
    system: str = "mks",
) -> UnitRegistry:
    # ureg = UnitRegistry(system='mks', non_int_type=Decimal)
    # ureg = UnitRegistry(system='mks')
    ureg = UnitRegistry(system=system)
    ureg.enable_contexts(
        "Gaussian", "ESU", "sp", "energy", "boltzmann"
    )  # https://github.com/hgrecco/pint/issues/1205

    # https://en.wikipedia.org/wiki/Ell
    ureg = add_unit_to_ureg(
        ureg=ureg,
        unit_name="ell",
        unit_def="45 * inch",
        unit_symbol="_",
        unit_aliases=[],
        verbose=verbose,
    )
    ureg = add_unit_to_ureg(
        ureg=ureg,
        unit_name="scottish_ell",
        unit_def="37 * inch",
        unit_symbol="_",
        unit_aliases=[],
        verbose=verbose,
    )

    # https://en.wikipedia.org/wiki/Ancient_Egyptian_units_of_measurement
    # https://www.youtube.com/watch?v=jyFkBaKARAs
    # pi/6
    ureg = add_unit_to_ureg(
        ureg=ureg,
        unit_name="royal_cubit",
        unit_def="52.3 * cm",
        unit_symbol="_",
        unit_aliases=[],
        verbose=verbose,
    )
    # 14624 "sutu?" is 527km https://www.youtube.com/watch?v=s_fkpZSnz2I @ 18:45

    ## unitcalc.unitcalc.UnitAlreadyDefinedError: amps
    # ureg = add_unit_to_ureg(ureg=ureg,
    #                        unit_name='amps',
    #                        unit_def='1 * amp',
    #                        unit_symbol='_',
    #                        unit_aliases=[],
    #                        verbose=verbose,
    #                        )

    ureg = add_unit_to_ureg(
        ureg=ureg,
        unit_name="fiftybmg",  # ~18kJ
        unit_def="18050 * joules",
        unit_symbol="_",
        unit_aliases=[],
        verbose=verbose,
    )
    ureg = add_unit_to_ureg(
        ureg=ureg,
        unit_name="Watts",
        unit_def="W",
        unit_symbol="_",
        unit_aliases=[],
        verbose=verbose,
    )
    ic(type(ureg))
    return ureg


def find_unit(
    *,
    ulist,
    in_unit,
    verbose: Union[bool, int, float],
):

    distance = -1
    ic(type(ulist))
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


def convert_atom_to_pint(
    atom,
    *,
    ureg: UnitRegistry,
    verbose: Union[bool, int, float],
):

    if verbose:
        ic(atom)

    # this might need to be earlier
    if not atom[0].isdigit():
        if atom[0] == ".":
            atom = "0" + atom

    # find the end of the magnitude
    index = None
    for index, letter in enumerate(atom):
        if letter.isalpha():  # ",".isalpha() == False (and .)
            if letter == "e":
                if not atom[index + 1].isdigit():
                    break
            else:
                break

    if verbose:
        ic(atom)

    if index:
        magnitude = atom[:index].replace(",", "")  # code duplicated elsewhere
        try:
            magnitude = Decimal(magnitude)
        except ValueError as e:
            # should use https://github.com/sopel-irc/sopel/blob/master/sopel/tools/calculation.py
            # or sage
            if verbose:
                ic(e)
            expression_pattern = re.compile(r"[0-9/\*e.+\-()]")
            for item in magnitude:
                assert expression_pattern.match(item)

            if verbose:
                ic(magnitude)

            assert magnitude[0].isdigit()
            magnitude = Decimal(eval(magnitude))
    else:
        magnitude = atom

    unit = atom[index:]

    if verbose:
        ic(magnitude)
        ic(unit)

    try:
        atom_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        if verbose:
            ic(e)
        found_unit = find_unit(
            ulist=dir(ureg),
            in_unit=unit,
            verbose=verbose,
        )
        if verbose:
            ic(found_unit)
        atom_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    atom_parsed = Q_(magnitude, atom_target)

    if verbose:
        ic(atom_parsed)

    return atom_parsed


def normalize_whitespace(
    *,
    string: str,
    verbose: Union[bool, int, float],
):

    # normalize whitespace to single space
    string = string.split(" ")
    string = " ".join([i for i in string if i])
    return string


# remove duplicate spaces, convert words to numbers
def normalize_human_input(
    *,
    human_input: str,
    verbose: Union[bool, int, float],
):
    if verbose:
        ic(human_input)

    human_input = normalize_whitespace(
        string=human_input,
        verbose=verbose,
    )

    if verbose:
        ic(human_input)

    words = []
    for word in human_input.split(" "):
        # ic(word)
        converted_word = parse_number(word)
        # ic(converted_word)
        if converted_word:
            words.append(str(converted_word))  # numbers [/d] come back as ints
        else:
            words.append(word)

    # ic(words)
    human_input = " ".join(words)
    # ic(human_input)

    if verbose:
        ic(human_input)

    return human_input


# todo, make sure scientific notation and equations work
# must be after words are converted to numbers
def split_human_input_on_numbers(
    *,
    human_input: str,
    verbose: Union[bool, int, float],
):
    if verbose:
        ic(human_input)

    human_input = "".join(human_input.split(","))  # strip commas

    list_of_human_input_atoms = re.findall(r"[\d\.]+\.?[^\d\.]+", human_input)
    if verbose:
        ic(list_of_human_input_atoms)
    return list_of_human_input_atoms


# this takes a arb string, which could be many atoms, and yields pint atoms
def generate_pint_atoms_from_string(
    *,
    human_input: str,
    ureg,
    verbose: Union[bool, int, float],
):

    human_input = normalize_human_input(
        human_input=human_input,
        verbose=verbose,
    )
    if verbose:
        ic(human_input)

    # at this point, the string is [number] [space] [unit description] so split on numbers

    human_input_atoms = split_human_input_on_numbers(
        human_input=human_input,
        verbose=verbose,
    )

    for atom in human_input_atoms:
        pint_atom = convert_atom_to_pint(
            atom=atom,
            ureg=ureg,
            verbose=verbose,
        )

        yield pint_atom


# this is the last step
def convert_pint_atom_to_unit(
    *,
    pint_atom,
    to_unit_string: str,
    ureg: UnitRegistry,
    verbose: Union[bool, int, float],
):

    assert not to_unit_string[0].isdigit()

    if verbose:
        ic(pint_atom, to_unit_string)

    try:
        to_unit_string_target = ureg.parse_units(to_unit_string)
    except UndefinedUnitError as e:
        if verbose:
            ic("UndefinedUnitError:", e)

        found_unit = find_unit(
            ulist=dir(ureg),
            in_unit=to_unit_string,
            verbose=verbose,
        )
        to_unit_string_target = ureg.parse_units(found_unit)

    if verbose:
        ic(pint_atom, to_unit_string_target)

    # if '±' in pint_atom:
    #    ic(pint_atom)
    # ic(dir(pint_atom))

    fromq_converted = pint_atom.to(to_unit_string_target)
    if verbose:
        ic(fromq_converted)
        ic(fromq_converted.magnitude)

    return fromq_converted


def combine_human_input_to_single_quantity(
    quantity,
    *,
    verbose: Union[bool, int, float],
    ureg: object,
):
    atoms = []
    for atom in generate_pint_atoms_from_string(
        human_input=quantity,
        ureg=ureg,
        verbose=verbose,
    ):

        if verbose:
            ic(atom)
        atom = atom.to_base_units()
        atoms.append(atom)

    summed_atoms = atoms[0]
    for atom in atoms[1:]:
        summed_atoms += atom

    return summed_atoms


def convert(
    *,
    human_input_units: str,
    human_output_unit: str,
    verbose: Union[bool, int, float],
    ureg: Optional[UnitRegistry] = None,
):

    if not ureg:
        ureg = construct_unitregistry(
            system="mks",
            verbose=verbose,
        )

    summed_atoms = combine_human_input_to_single_quantity(
        quantity=human_input_units,
        ureg=ureg,
        verbose=verbose,
    )
    fromq_converted = convert_pint_atom_to_unit(
        pint_atom=summed_atoms,
        to_unit_string=human_output_unit,
        ureg=ureg,
        verbose=verbose,
    )

    return fromq_converted


@click.command()
@click.argument("quantity", required=True)
@click.argument("to_units", nargs=-1)
@click.option("--ipython", is_flag=True)
@click_add_options(click_global_options)
def cli(
    quantity: str,
    to_units: str,
    verbose: Union[bool, int, float],
    verbose_inf: bool,
    dict_input: bool,
    ipython: bool,
):

    if verbose:
        ic(quantity, to_units)

    ureg = construct_unitregistry(
        system="mks",
        verbose=verbose,
    )
    summed_atoms = combine_human_input_to_single_quantity(
        quantity=quantity,
        ureg=ureg,
        verbose=verbose,
    )
    if not to_units:
        if verbose:
            ic(summed_atoms)
            ic(summed_atoms.to_base_units())
        print(summed_atoms)
        return

    for unit in to_units:
        if verbose:
            ic(unit)
        fromq_converted = convert_pint_atom_to_unit(
            pint_atom=summed_atoms,
            to_unit_string=unit,
            ureg=ureg,
            verbose=verbose,
        )

        ic(fromq_converted)
        print(fromq_converted)

    if ipython:
        import IPython

        IPython.embed()
