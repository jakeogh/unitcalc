#!/usr/bin/env python3
# -*- coding: utf8 -*-

# pylint: disable=useless-suppression             # [I0021]
# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=missing-param-doc               # [W9015]
# pylint: disable=missing-module-docstring        # [C0114]
# pylint: disable=fixme                           # [W0511] todo encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-many-public-methods         # [R0904]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement
from __future__ import annotations

import contextlib
import re
from decimal import Decimal
from decimal import InvalidOperation

import uncertainties
from asserttool import ic
from eprint import eprint
from Levenshtein import StringMatcher
from number_parser import parse_number
from pint import UnitRegistry  # slow import
from pint.errors import UndefinedUnitError
from unittool import UnitAlreadyDefinedError
from unittool import construct_unit_registry


def get_all_unit_names(ureg):
    all_names = set(dir(ureg))


def human_filesize_to_int(
    size: str,
    *,
    verbose: bool | int | float = False,
):
    u = UnitRegistry()
    i = u.parse_expression(size)
    result = i.to("bytes").magnitude
    # result = int(result)
    ic(result)
    return int(result)


def find_unit(
    *,
    ulist,
    in_unit,
    verbose: bool | int | float = False,
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
    eprint(f"Warning: converting {in_unit} to {winning_unit}")
    return winning_unit


def convert_atom_to_magnitude_and_unit(atom):
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

    ic(atom)

    if index:
        magnitude = atom[:index].replace(",", "")  # code duplicated elsewhere
        ic(magnitude)
        try:
            magnitude = Decimal(magnitude)
        except (ValueError, InvalidOperation) as e:
            # should use https://github.com/sopel-irc/sopel/blob/master/sopel/tools/calculation.py
            # or sage
            ic(e)
            expression_pattern = re.compile(r"[0-9/\*e.\*+\-()]")
            for item in magnitude:
                ic(item)
                assert expression_pattern.match(item)

            ic(magnitude)

            assert magnitude[0].isdigit()
            magnitude = Decimal(eval(magnitude))
    else:
        magnitude = atom

    unit = atom[index:]

    return magnitude, unit


def convert_atom_to_pint(
    atom,
    *,
    ureg: UnitRegistry,
    verbose: bool | int | float = False,
):
    ic(atom)

    magnitude, unit = convert_atom_to_magnitude_and_unit(atom)

    ic(magnitude)
    ic(unit)

    try:
        atom_target = ureg.parse_units(unit)
    except UndefinedUnitError as e:
        ic(e)
        found_unit = find_unit(
            ulist=dir(ureg),
            in_unit=unit,
        )
        ic(found_unit)
        atom_target = ureg.parse_units(found_unit)

    Q_ = ureg.Quantity
    atom_parsed = Q_(magnitude, atom_target)

    ic(atom_parsed)
    return atom_parsed


def normalize_whitespace(
    *,
    string: str,
    verbose: bool | int | float = False,
):
    # normalize whitespace to single space
    string = string.split(" ")
    string = " ".join([i for i in string if i])
    return string


# remove duplicate spaces, convert words to numbers
def normalize_human_input(
    *,
    human_input: str,
    verbose: bool | int | float = False,
):
    ic(human_input)

    human_input = normalize_whitespace(
        string=human_input,
    )

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

    ic(human_input)

    return human_input


# todo, make sure scientific notation and equations work
# must be after words are converted to numbers
def split_human_input_on_numbers(
    *,
    human_input: str,
    verbose: bool | int | float = False,
):
    ic(human_input)

    human_input = "".join(human_input.split(","))  # strip commas
    human_input = human_input.replace("^", "**")

    list_of_human_input_atoms = re.findall(r"[\d\.\*]+\.?[^\d\.]+", human_input)
    ic(list_of_human_input_atoms)
    return list_of_human_input_atoms


# this takes a arb string, which could be many atoms, and yields pint atoms
def generate_pint_atoms_from_string(
    *,
    human_input: str,
    ureg,
    verbose: bool | int | float = False,
):
    human_input = normalize_human_input(
        human_input=human_input,
    )
    ic(human_input)

    # at this point, the string is [number] [space] [unit description] so split on numbers

    human_input_atoms = split_human_input_on_numbers(
        human_input=human_input,
    )

    for atom in human_input_atoms:
        pint_atom = convert_atom_to_pint(
            atom=atom,
            ureg=ureg,
        )

        yield pint_atom


# this is the last step
def convert_pint_atom_to_unit(
    *,
    pint_atom,
    to_unit_string: str,
    ureg: UnitRegistry,
    verbose: bool | int | float = False,
):
    assert not to_unit_string[0].isdigit()

    ic(pint_atom, to_unit_string)

    try:
        to_unit_string_target = ureg.parse_units(to_unit_string)
    except UndefinedUnitError as e:
        ic("UndefinedUnitError:", e)

        found_unit = find_unit(
            ulist=dir(ureg),
            in_unit=to_unit_string,
        )
        to_unit_string_target = ureg.parse_units(found_unit)

    ic(pint_atom, to_unit_string_target)

    # if '±' in pint_atom:
    #    ic(pint_atom)
    # ic(dir(pint_atom))

    fromq_converted = pint_atom.to(to_unit_string_target)
    ic(fromq_converted)
    ic(fromq_converted.magnitude)

    return fromq_converted


def combine_human_input_to_single_quantity(
    quantity,
    *,
    verbose: bool | int | float = False,
    ureg: object,
):
    atoms = []
    for atom in generate_pint_atoms_from_string(
        human_input=quantity,
        ureg=ureg,
    ):
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
    verbose: bool | int | float = False,
    ureg: UnitRegistry | None = None,
):
    if not ureg:
        ureg = construct_unit_registry(
            system="mks",
        )

    summed_atoms = combine_human_input_to_single_quantity(
        quantity=human_input_units,
        ureg=ureg,
    )
    fromq_converted = convert_pint_atom_to_unit(
        pint_atom=summed_atoms,
        to_unit_string=human_output_unit,
        ureg=ureg,
    )

    return fromq_converted


# from pint_convery.py
def use_unc(num, fmt, prec_unc):
    unc = 0
    with contextlib.suppress(Exception):
        if isinstance(num, uncertainties.UFloat):
            full = ("{:" + fmt + "}").format(num)
            unc = re.search(r"\+/-[0.]*([\d.]*)", full).group(1)
            unc = len(unc.replace(".", ""))

    return max(0, min(prec_unc, unc))


# from pint_convery.py
def _convert(*, ureg, u_from, reason: bool, u_to=None, unc=None, factor=None):
    args_prec = 12
    args_prec_unc = 2
    ic(u_from, u_to)
    q = ureg.Quantity(u_from)
    fmt = f".{args_prec}g"
    if unc:
        q = q.plus_minus(unc)
    if u_to:
        nq = q.to(u_to)
    else:
        nq = q.to_base_units()
    if factor:
        q *= ureg.Quantity(factor)
        nq *= ureg.Quantity(factor).to_base_units()
    prec_unc = use_unc(nq.magnitude, fmt, args_prec_unc)
    if prec_unc > 0:
        fmt = f".{prec_unc}uS"
    else:
        with contextlib.suppress(Exception):
            nq = nq.magnitude.n * nq.units

    fmt = "{:" + fmt + "} {:~P}"
    ic(fmt, q, nq.magnitude, nq.units)
    if reason:
        _output = ("{:} = " + fmt).format(q, nq.magnitude, nq.units)
    else:
        _output = (fmt).format(nq.magnitude, nq.units)
    ic(_output)
    # print(_output)
    return _output
