"""A class that loads and parses diamond electronic defects to be included when solving for the band structure."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
from scipy.interpolate import interp1d
from scipy.integrate import trapz
from scipy.special import expit
from scipy.interpolate import CubicSpline
from diamond_bandalyzer.settingsobject import SettingsObject, config_folder, config_parser_args
import diamond_bandalyzer.fundementalconstants as fc
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from diamond_bandalyzer.utilities import ini_string_to_python

from . import LENGTH_SCALE, ENERGY_SCALE

if not config_folder.exists():
    print(f"Couldn't find .config folder!")

defect_library = config_folder / "defect_library.ini"
library_parser = ConfigParser(**config_parser_args)

# make sure we have a default settings file
if not defect_library.exists():
    print(f"Couldn't find {str(defect_library)}, only user defined defects can be used!")
else:
    with open(defect_library) as f:
        library_parser.read_file(f)


def energies_from_library(name):
    try:
        donor_energy = library_parser.getfloat(name, 'donor_energy')
    except NoOptionError:
        donor_energy = None
    try:
        acceptor_energy = library_parser.getfloat(name, 'acceptor_energy')
    except NoOptionError:
        acceptor_energy = None
    if donor_energy is None and acceptor_energy is None:
        raise NoSectionError
    try:
        subband_width = library_parser.getfloat(name, 'subband_width')
    except NoOptionError:
        subband_width = None
    return {'donor_energy': donor_energy, 'acceptor_energy': acceptor_energy, 'subband_width': subband_width}


def parse_defect_addition(name, donor_energy=None, acceptor_energy=None, subband_width=None, density_file=None, density_ranges=None,
                          defect_densities=None, vol_surf_densities=None):
    if donor_energy is None and acceptor_energy is None:
        try:
            default_energies = energies_from_library(name)
        except NoSectionError:
            # TODO log as warning.
            print(f"Warning: defect '{name}' has neither donor, nor acceptor transition energies defined in defects.ini"
                  f"or in default defects library and will be ignored.")
            return
        else:
            donor_energy = default_energies['donor_energy']
            acceptor_energy = default_energies['acceptor_energy']
            try:
                subband_width = default_energies['subband_width']
            except:
                pass

    if density_file is None and defect_densities is None:
        # TODO log as warning.
        print(f"Warning: defect '{name}' has neither file nor array density definition in defects.ini and will be "
              f"ignored.")
        return

    if density_file is None:
        for i in range(len(density_ranges)):
            if np.size(density_ranges[i]) == 1:
                density_ranges[i] = [density_ranges[i], density_ranges[i]]
        density_ranges = np.array(density_ranges)
        if len(density_ranges.shape) == 1:
            density_ranges = np.array([density_ranges])
        if not np.shape(defect_densities):
            defect_densities = np.array([defect_densities])
        if len(defect_densities) != density_ranges.shape[0]:
            if len(defect_densities) > 1:
                print(f"Warning: Cannot determined desired defect box density for {name} as number of ranges doesnt "
                      "match with multiple provided densities.  This defect will be ignored")
                return
            else:
                print(f"Warning: One density for {name} provided, assuming every range has same density.")
                defect_densities = np.repeat(defect_densities, density_ranges.shape[0])

    for n, d_range in enumerate(density_ranges):
            density_ranges[n] = np.array([np.min(d_range), np.max(d_range)])

    if vol_surf_densities is None:
        print(f"Warning: defect '{name}' has not had its density type (surface vs. volumetric) specified and will "
              "default to volumentric density.")
        vol_surf_densities = np.zeros((len(density_ranges.shape)))
    parsed_defect_dict = {}
    for p_name, param in zip(['donor_energy', 'acceptor_energy', 'subband_width', 'density_file', 'density_ranges',
                              'defect_densities','vol_surf_densities'],
                             [donor_energy, acceptor_energy, subband_width, density_file, density_ranges,
                              defect_densities, vol_surf_densities]):
        if param is not None:
            parsed_defect_dict[p_name] = param

    return parsed_defect_dict


class Defects(SettingsObject):
    _settings_heading_ = "DefectDefinition"
    default_settings = {'density_file_comments': '#', 'temperature_k': 300,
                        'subband_convolution_v_linspace': [-5.4, 5.4, 10000],
                        'subband_convolution_variable_bounds_multiplier': 7.6, 'subband_convolution_variable_step': 0.01}

    def __init__(self, defects_ini=None, defect_dict=None, length_units='cm', **kwargs):
        super().__init__(**kwargs)
        self.__add_default_settings__(Defects, **kwargs)
        self.length_units = length_units
        self.length_scale = fc.Scale(LENGTH_SCALE, length_units)()
        self.areal_scale = self.length_scale**-2
        self.density_scale = self.length_scale**-3
        self.energy_scale = fc.Scale(ENERGY_SCALE, 'eV')()

        self.kT = fc.k * self.settings['temperature_k']
        self.defect_dict = {}
        if defect_dict is not None:
            self.__unpack_defect_dict__(defect_dict)

        if defects_ini is not None:
            try:
                self.add_defects_from_ini(Path(defects_ini))
            except FileNotFoundError:
                if 'local_dir' in self.settings:
                    init_path = Path(self.settings['local_dir']) / defects_ini
                else:
                    init_path = Path('defects.ini')
                try:
                    self.add_defects_from_ini(init_path)
                except FileNotFoundError:
                    # TODO log as warning
                    print(f"defects.ini not found at the following locations:\n{Path(defects_ini.absolute())}\n"
                          f"{init_path.absolute()}\n{(Path(self.settings['local_dir']) / defects_ini).absolute()}")




    def __unpack_defect_dict__(self, defect_dict):
        if defect_dict is None:
            return
        for name, this_defect_dict in defect_dict.items():
            self.add_defect(name, **this_defect_dict)
            # self.defects[name] = {'E': E, 'N': N, 'donor': bool(donor), 'bulk': bool(bulk)}

    def add_defects_from_ini(self, ini_file):
        """Adds defects to the solver from an ini_file.  This need not be called directly, and the solver will
        search for a defects.ini upon instansation.  Use this function if a differently named ini file is to be used.

        The ini file syntax is section headings haveing the defect short name, and then the desired sections listed
        as options. e.g.

        [NV]
        donor_energy=0.75 ; Optional, will look in defect library
        acceptor_energy=2.85
        density_file=ImplantProfileNV ; Either this or the other two must be specified.
        density_ranges=[[0,2],[0,3]]
        defect_densities=[1e15,1e10]

        A name and either a density file or density range and density must be provided."""
        ini_parser = ConfigParser(**config_parser_args)
        with open(ini_file, mode='r') as f:
            ini_parser.read_file(f)
        for name in ini_parser.sections():
            load = {}
            for option in ['donor_energy', 'acceptor_energy', 'subband_width' , 'density_file', 'density_ranges', 'defect_densities', 'vol_surf_densities']:
                try:
                    load[option] = ini_string_to_python(ini_parser.get(name, option))
                except NoOptionError:
                    pass
            parsed_dict = parse_defect_addition(name, **load)
            if parsed_dict:
                if name in self.defect_dict:
                    # TODO log warning
                    print(f"Overwriting pre-existing definition for {name} with ini file definition.\n"
                          f"Original Definition:\n{self.defect_dict[name]}\n\n"
                          f"New Definition:\n{parsed_dict}")
                self.defect_dict[name] = parsed_dict

    def add_defect(self, name, donor_energy=None, acceptor_energy=None, subband_width=None, density_file=None, density_ranges=None,
                   defect_densities=None, vol_surf_densities=None):
        """Adds defects to the solver, this can be achieved in three ways. In recommended order.
         1. Define a defects.ini in the local directory or pass a differently names ini to add_defects_from_ini.  See
         the function description for required ini structure.

         2. At class instance creation by passing parameters in as a dict with this structure:
         {'name': {'donor_energy', 'acceptor_energy', 'subband_width', 'density_file', 'density_ranges', 'defect_densities', 'vol_surf_densities'}}

        3. Adding each defect individually via this function."""

        if name not in self.defect_dict:
            parsed_dict = parse_defect_addition(name, donor_energy, acceptor_energy, subband_width, density_file,
                                                density_ranges, defect_densities, vol_surf_densities)
            if parsed_dict:
                if name in self.defect_dict:
                    # TODO log warning
                    print(f"Overwriting pre-existing definition for {name} with function call definition."
                          f"Original Definition:\n{self.defect_dict[name]}\n\n"
                          f"New Definition:\n{parsed_dict}")
                self.defect_dict[name] = parsed_dict

    def get_defect_transition_energies_and_densities(self, z_mesh):
        defect_densities = np.zeros((len(self.defect_dict), len(z_mesh)))
        density_non_zeros = []
        donor_transitions = {}
        acceptor_transitions = {}

        for n, (name, this_defect_dict) in enumerate(self.defect_dict.items()):
            if 'density_file' in this_defect_dict:
                density_data = np.loadtxt('density_file', comments=self.settings['density_file_comments'])
                if density_data.shape[0] > density_data.shape[1]:
                    defect_densities[n] = interp1d(*density_data.T, bounds_error=False, fill_value=0)(z_mesh)*self.density_scale
                else:
                    defect_densities[n] = interp1d(*density_data, bounds_error=False, fill_value=0)(z_mesh)*self.density_scale
            else:
                for (lower, upper), density, vol_surf in zip(this_defect_dict['density_ranges'],
                                                   this_defect_dict['defect_densities'], this_defect_dict['vol_surf_densities']):
                    if vol_surf == 0: #Volumentric density case
                        defect_densities[n][(z_mesh >= lower*self.length_scale) & (z_mesh <= upper*self.length_scale)] += float(density)*self.density_scale
                    else: #Surface/areal density case - this formula applies for TRAPEZOIDAL INTEGRATION ONLY - different formulae needed for quadratic integral approximation
                        if lower != upper:
                            print(f'Warning: A finite-width region has been specified for an areal defect density assigned to defect: {name}. Defaulting to the lower specified depth.')
                        surfIndex = [i for i, n in enumerate(z_mesh) if (n >= lower*self.length_scale) & (n <= upper*self.length_scale)]
                        surfIndex = surfIndex[0] #Default to the 'shallowest' point if the specified depth falls between two mesh indices
                        if surfIndex == 0: #If the specified layer happens to be at the end of the domain
                            defect_densities[n][surfIndex] = float(density) * self.density_scale / (
                                        z_mesh[surfIndex + 1] - z_mesh[surfIndex])
                        elif surfIndex == len(z_mesh)-1: #If the specified layer is at the back surface
                            defect_densities[n][surfIndex] = float(density) * self.density_scale / (
                                        z_mesh[surfIndex] - z_mesh[surfIndex - 1])
                        else: #General case
                            defect_densities[n][surfIndex] = 2 * float(density) * self.density_scale / (
                                        z_mesh[surfIndex + 1] - z_mesh[surfIndex - 1])
                density_non_zeros.append(np.nonzero(defect_densities[n])[0])
            if 'acceptor_energy' in this_defect_dict:
                if 'subband_width' not in this_defect_dict:
                    acceptor_transitions[name] = [this_defect_dict['acceptor_energy']*self.energy_scale, defect_densities[n],
                                                density_non_zeros[n], None, None, None]
                else:
                    if this_defect_dict['subband_width'] == 0:
                        acceptor_transitions[name] = [this_defect_dict['acceptor_energy'] * self.energy_scale,
                                                      defect_densities[n],
                                                      density_non_zeros[n], None, None, None]
                    else:
                        spline = self.__generate_subband_spline__(this_defect_dict['subband_width'])
                        acceptor_transitions[name] = [this_defect_dict['acceptor_energy'] * self.energy_scale,
                                                      defect_densities[n],
                                                      density_non_zeros[n], this_defect_dict['subband_width'], spline[0], spline[1]]
            if 'donor_energy' in this_defect_dict:
                if 'subband_width' not in this_defect_dict:
                    donor_transitions[name] = [this_defect_dict['donor_energy']*self.energy_scale, defect_densities[n], density_non_zeros[n], None, None, None]
                else:
                    if this_defect_dict['subband_width'] == 0:
                        donor_transitions[name] = [this_defect_dict['donor_energy'] * self.energy_scale,
                                                   defect_densities[n], density_non_zeros[n], None, None, None]
                    else:
                        spline = self.__generate_subband_spline__(this_defect_dict['subband_width'])
                        donor_transitions[name] = [this_defect_dict['donor_energy'] * self.energy_scale,
                                                      defect_densities[n],
                                                      density_non_zeros[n], this_defect_dict['subband_width'], spline[0],
                                                      spline[1]]

        return defect_densities, density_non_zeros, donor_transitions, acceptor_transitions

    def __generate_subband_spline__(self, subband_width):
        fwhm = subband_width*self.energy_scale
        c = fwhm / (2 * np.sqrt(2 * np.log(2)))
        test_v = np.linspace(*self.settings['subband_convolution_v_linspace'])*self.energy_scale / self.kT
        bound = fwhm * self.settings['subband_convolution_variable_bounds_multiplier']
        energies = np.arange(-bound, bound, self.settings['subband_convolution_variable_step']*self.energy_scale)
        y = np.zeros_like(test_v)
        for n, V in enumerate(test_v):
            y[n] = trapz(expit(energies / self.kT + V) * np.exp(-energies ** 2 / (2 * c ** 2)), energies)
        y = y / (np.sqrt(2 * np.pi) * c)
        subband_spline = CubicSpline(test_v, y)
        return subband_spline, subband_spline.derivative(1)

    def get_top_surface(self, Qexternal):
        return lambda x: Qexternal*self.areal_scale
                         #+ self.settings['top_sp2_defect_density'] * self.areal_scale \
                         #* self.sp2_spline(-self.settings['sp2_defect_energy']*self.energy_scale / self.kT + x)

    def get_back_surface(self, Qexternal):
        return lambda x: Qexternal*self.areal_scale
                         #+ self.settings['back_sp2_defect_density'] * self.areal_scale \
                         #* self.sp2_spline(-self.settings['sp2_defect_energy']*self.energy_scale / self.kT + x)

    def save_jsoncache(self, **kwargs):
        # Extend the save function to get our defect dict into the jsoncache file.
        self.settings['defect_dict'] = self.defect_dict
        return super().save_jsoncache(**kwargs)


    def get_top_surface_deriv(self):
        return lambda x: self.settings['top_sp2_defect_density'] * self.areal_scale \
                         * self.sp2_spline_deriv(-self.settings['sp2_defect_energy']*self.energy_scale / self.kT + x)

    def get_back_surface_deriv(self):
        return lambda x: self.settings['back_sp2_defect_density'] * self.areal_scale \
                         * self.sp2_spline_deriv(-self.settings['sp2_defect_energy']*self.energy_scale / self.kT + x)
