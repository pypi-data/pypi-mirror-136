"""Module providing the fundamental constants of the universe."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

from . import SOLVER_UNIT_SYSTEM, LENGTH_SCALE, ENERGY_SCALE
from numpy import pi


class Scale:

    def __init__(self, output_scale, input_scale=None):
        vars_dict = {'length': {'nm': 1e-9, 'mm': 1e-3, 'cm': 1e-2, 'm': 1, 'a0': 5.29177210903e-11, 'ka0': 5.29177210903e-11 * 1e3, 'A': 1e-10, 'um': 1e-6},
                     'energy': {'eV': 1, 'J': 6.241509e18, 'Eh': 27.211386245988, 'ev': 1},
                     'potential': {'V': 1, 'Eh/e': 27.211386245988},
                     'charge': {'C': 1/1.602E-19, 'e': 1}}
        self.scale = None
        self.units_dict = None
        for vars, units_dict in vars_dict.items():
            if output_scale in units_dict:
                self.out_scale = units_dict[output_scale]
                self.units_dict = units_dict
            if input_scale in units_dict:
                self.scale = self.__call__(in_scale=input_scale)
                break

    def __call__(self, in_scale=None):
        if in_scale is None:
            return self.scale
        try:
            return float(self.units_dict[in_scale]) / float(self.out_scale)
        except KeyError:
            try:
                return float(in_scale) / float(self.out_scale)
            except TypeError:
                raise TypeError(f"Cannot interpret {in_scale} as known unit string or float.")


alpha = 0.0072973525693  # (11) Fine structure constant

if SOLVER_UNIT_SYSTEM == 'hartree-atomic':
    length_scale = Scale(LENGTH_SCALE)
    energy_scale = Scale(ENERGY_SCALE)
    h_bar = 1.0  # reduced planks constant
    e = 1.0  # charge on an electron
    mo = 1.0 / length_scale('a0')**2  # mass of an electron
    a0 = 1.0  # bhor radius
    h = 2 * pi * h_bar  # hbar
    c = 1.0 / alpha  # a0Eh/hbar  Speed of light
    k = 8.6173303e-5 * energy_scale('eV')   # Eh / K
    epsilon0 = 1.0 / (4*pi) / length_scale('a0')  # 4pie^2/a0Eh  vacuum permittivity

else:  # SOLVER_UNIT_SYSTEM = 'legacy'
    length_scale = Scale(LENGTH_SCALE)
    k = 8.6173303e-5  # eV / K  Boltzmann constant
    h = 4.1357e-15  # eV s  Planks constant
    h_bar = h / (2 * pi) # eV s  reduced planks constant
    c = 3E10 * length_scale('cm')  # cm/s  Speed of light  # Z scale dependent.
    mo = 5.11e5/(c**2)  # eV c^-2  mass of an electron
    epsilon0 = 1.4184409e-32 / length_scale('cm')  # C^2/eVcm  vacuum permittivity  # Z scale dependent.
    e = 1.602E-19  # C  charge on an electron
    a0 = 4 * pi * epsilon0 * h_bar ** 2 / (mo * e ** 2)
