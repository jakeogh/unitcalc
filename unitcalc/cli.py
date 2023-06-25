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

import click
from asserttool import ic
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from unittool import construct_unit_registry

from unitcalc import _convert
from unitcalc import combine_human_input_to_single_quantity
from unitcalc import convert_pint_atom_to_unit


@click.command()
@click.argument("quantity", required=True)
@click.argument("to_units", nargs=-1)
@click.option("--ipython", is_flag=True)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    *,
    quantity: str,
    to_units: str,
    verbose_inf: bool,
    dict_output: bool,
    ipython: bool,
    verbose: bool | int | float = False,
):
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )

    if not verbose:
        ic.disable()

    ic(quantity, to_units)

    ureg = construct_unit_registry(
        system="mks",
    )
    summed_atoms = combine_human_input_to_single_quantity(
        quantity=quantity,
        ureg=ureg,
    )

    if not to_units:
        ic(summed_atoms)
        ic(summed_atoms.to_base_units())
        # print(summed_atoms)
        _converted = _convert(ureg=ureg, u_from=summed_atoms, reason=False)
        print(_converted)
        return

    for unit in to_units:
        ic(summed_atoms, unit)
        fromq_converted = convert_pint_atom_to_unit(
            pint_atom=summed_atoms,
            to_unit_string=unit,
            ureg=ureg,
        )

        ic(fromq_converted)
        # print(fromq_converted)
        _converted = _convert(
            ureg=ureg, u_from=summed_atoms, u_to=fromq_converted, reason=True
        )
        print(_converted)

    if ipython:
        import IPython

        IPython.embed()
