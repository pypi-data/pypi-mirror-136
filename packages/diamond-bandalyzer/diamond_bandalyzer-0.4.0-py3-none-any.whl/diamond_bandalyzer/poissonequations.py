"""Class that provides functions that cover the equations required to solve Poissons Equation on a diamond."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import fdint
import traceback
from scipy.integrate import cumtrapz, trapz
from scipy.special import expit
from scipy.optimize import brentq
from .defects import Defects
from .settingsobject import SettingsObject
from . import ENERGY_SCALE
import diamond_bandalyzer.fundementalconstants as fc



class PoissonEquations(SettingsObject):
    _settings_heading_ = "PoissonEquations"
    default_settings = {'temperature_k': 300, 'epsilond': 5.8,
                        'diamond_electron_mass': 0.22, 'diamond_light_hole_mass': 0.303,
                        'diamond_heavy_hole_mass': 0.588,
                        'diamond_splitoff_hole_mass': 0.394, 'splitoff_hole_delta_energy': 0.006,
                        'diamond_band_gap': 5.45, 'fermi_solve_brentq_tol': 1e-10}

    def __init__(self, z_mesh=None, defects=None, Qext_top=None, Qext_back=None, **kwargs):
        super().__init__(**kwargs)
        self.__add_default_settings__(PoissonEquations, **kwargs)
        # ++ Arguments ++ #
        if not hasattr(self, 'z_mesh'):  # might already have this from multiple inheritance with a solver.
            self.z_mesh = z_mesh
        self.kT = fc.k * self.settings['temperature_k']
        self.energy_scale = fc.Scale(ENERGY_SCALE, 'eV')()
        # ++ Constants ++ #
        self.constEtoV = fc.e / self.kT  # constant for e-field from v
        self.constRhotoE = -fc.e / (fc.epsilon0 * self.settings['epsilond'])  # constant for charge density from e-field
        self.constRhotoV = self.constEtoV * self.constRhotoE
        self.me = self.settings['diamond_electron_mass'] * fc.mo
        self.mhh = self.settings['diamond_heavy_hole_mass'] * fc.mo
        self.mhl = self.settings['diamond_light_hole_mass'] * fc.mo
        self.mso = self.settings['diamond_splitoff_hole_mass'] * fc.mo
        self.delSO = self.settings['splitoff_hole_delta_energy'] * self.energy_scale
        self.NC = 2 * (2 * np.pi * self.me * self.kT / fc.h ** 2) ** (3 / 2)  # near edge conduction band density
        self.NVh = 2 * ((2 * np.pi * self.mhh * self.kT / fc.h ** 2) ** (3 / 2))
        self.NVl = 2 * ((2 * np.pi * self.mhl * self.kT / fc.h ** 2) ** (3 / 2))
        self.NV = self.NVh + self.NVl    # near edge valence band density
        self.NVso = 2 * (2 * np.pi * self.mso * self.kT / fc.h ** 2) ** (3 / 2)
        self.Eg = self.settings['diamond_band_gap'] * self.energy_scale

        if Qext_top is None:
            Qext_top = 0.0
        if Qext_back is None:
            Qext_back = 0.0

        # ++  Load in defects from Defects class.  We don't store the class. ++ #
        if type(defects) is not Defects:
            raise TypeError(f"Passed defects type cannot be '{type(defects)}', must be {Defects}.  If you want a defect"
                            f"free diamond use an empty Defects().")

        self.top_surface_raw = defects.get_top_surface(Qext_top)  # Z scale dependent.
        self.back_surface_raw = defects.get_back_surface(Qext_back)  # Z scale dependent.
    #    self.top_surface_deriv_raw = defects.get_top_surface_deriv()  # Z scale dependent.
    #    self.back_surface_deriv_raw = defects.get_back_surface_deriv()  # Z scale dependent.

        # ++ don't garbage collect this data ++ #
        defect_data = defects.get_defect_transition_energies_and_densities(self.z_mesh)
        self.donor_transitions = defect_data[2]
        self.acceptor_transitions = defect_data[3]
        self.defect_densities = defect_data[0]
        self.density_non_zeros = defect_data[1]

        # self.Ef = self.__estimate_fermi_energy__()

    def top_surface(self):
        return self.top_surface_raw(None)

    def back_surface(self):
        return self.back_surface_raw(None)

 #   def top_surface_deriv(self, Ef, vs):
 #       return self.top_surface_deriv_raw((Ef / self.kT) - vs)

 #   def back_surface_deriv(self, Ef, vs):
 #       return self.back_surface_deriv_raw((Ef / self.kT) - vs)

    # TODO: test if cumtrapz sufficiently fast / sufficiently accurate
    def v_from_e_field(self, e_field):
        # Returns the band-bending function (nu) that corresponds to the given E field, sets lowest v to 0.
        calc_v = self.constEtoV * (cumtrapz(e_field, self.z_mesh, initial=0))
        return calc_v - np.min(calc_v)  # ensure constant of integration is 0.

    def e_field_from_rho(self, rho, vs, vbs):
        """Computes the electric field in the diamond by integrating from the surface inwards (includes the effect of
        the any surface acceptor layers)."""
        # Add the extra little contribution from the beginning and end of the domain
        extra_charge = 0.5 * (rho[0] * (np.abs(self.z_mesh[1] - self.z_mesh[0]))
                              - rho[-1] * (np.abs(self.z_mesh[-2] - self.z_mesh[-1])))
        integrated_charge = cumtrapz(rho, self.z_mesh, initial=0)

        return self.constRhotoE * (self.top_surface() - self.back_surface() - extra_charge
                                   - 2 * integrated_charge + integrated_charge[-1])

    def e_field_from_v(self, v, z):
        """Compute the electric field via second-order accurate central difference gradient of v, won't step
        relaxation wise as occurs when calculating e-field from rho."""
        return (1 / self.constEtoV) * np.gradient(v, z, edge_order=2)

    def electron_density(self, v, Ef):
        return self.NC * fdint.parabolic(((Ef - self.Eg) / self.kT) - v)

    def electron_density_deriv(self, v, Ef):
        return self.NC * fdint.dparabolic(((Ef - self.Eg) / self.kT) - v)

    def hole_density(self, v, Ef, **kwargs):
        # heavy, light and split-off hole bands
        return self.NV * fdint.parabolic((-(Ef / self.kT) + v)) \
               + self.NVso * fdint.parabolic((-(Ef + self.delSO) / self.kT) + v)

    def hole_density_deriv(self, v, Ef):
        # heavy light and split-off hole bands
        return self.NV * fdint.dparabolic((-(Ef / self.kT) + v)) \
               + self.NVso * fdint.dparabolic((-(Ef + self.delSO) / self.kT) + v)

    # TODO: check if speed difference between np.multiply and * operator. Can we use += operator for code-clarity?
    def total_charged_defect_density(self, v, Ef):
        """Returns the z dependent total charged defect density for a given v(z)."""
        total_char_density = np.zeros_like(self.z_mesh)

        for (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.donor_transitions.values():
            if subband_width is None:
             #   print(len(density_array[idx_non_zero]))
                total_char_density[idx_non_zero] = total_char_density[idx_non_zero] + np.multiply(
                    density_array[idx_non_zero], expit(v[idx_non_zero] - (Ef - transition_energy) / self.kT))
            else:
              #  print(density_array[idx_non_zero]*spline(-((-(Ef - transition_energy) / self.kT) + v[idx_non_zero])))
                total_char_density[idx_non_zero] = total_char_density[idx_non_zero] + np.multiply(
                    density_array[idx_non_zero], spline(((-(Ef - transition_energy) / self.kT) + v[idx_non_zero])))

        for (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.acceptor_transitions.values():
            if subband_width is None:
                total_char_density[idx_non_zero] = total_char_density[idx_non_zero] - np.multiply(
                    density_array[idx_non_zero], expit(-v[idx_non_zero] - (transition_energy - Ef) / self.kT))
            else:
                total_char_density[idx_non_zero] = total_char_density[idx_non_zero] - np.multiply(
                    density_array[idx_non_zero], spline(((Ef - transition_energy) / self.kT) - v[idx_non_zero]))

        return total_char_density

    def total_charged_defect_density_deriv(self, v, Ef):
        """Returns the z dependent total charged defect density derivative wrt v for a given v(z)."""
        total_char_density_deriv = np.zeros_like(self.z_mesh)

        for (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.donor_transitions.values():
            if subband_width is None:
                total_char_density_deriv[idx_non_zero] = total_char_density_deriv[idx_non_zero] + np.multiply(np.multiply(
                    density_array[idx_non_zero], expit(v[idx_non_zero] - (Ef - transition_energy) / self.kT)),
                    expit(-v[idx_non_zero] + (Ef - transition_energy) / self.kT))
            else:
                total_char_density_deriv[idx_non_zero] = total_char_density_deriv[idx_non_zero] + np.multiply(
                    density_array[idx_non_zero], spline_deriv(((-(Ef - transition_energy) / self.kT) + v[idx_non_zero])))

        for (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.acceptor_transitions.values():
            if subband_width is None:
                total_char_density_deriv[idx_non_zero] = total_char_density_deriv[idx_non_zero] + np.multiply(np.multiply(
                    density_array[idx_non_zero], expit(-v[idx_non_zero] - (transition_energy - Ef) / self.kT)),
                    expit(v[idx_non_zero] + (transition_energy - Ef) / self.kT))
            else:
                total_char_density_deriv[idx_non_zero] = total_char_density_deriv[idx_non_zero] + np.multiply(
                    density_array[idx_non_zero], spline_deriv(((Ef - transition_energy) / self.kT) - v[idx_non_zero]))

        return total_char_density_deriv

    def update_fermi_energy(self, v):
        oldEf = self.Ef
        try:
            self.Ef = brentq(self.integrated_charge, self.Ef - self.Eg, self.Ef + self.Eg,
                             args=v, xtol=self.settings['fermi_solve_brentq_tol'])
        except (RuntimeError, RuntimeWarning, TypeError, ValueError) as e:
            traceback.print_exc()
            self.Ef = oldEf
            pass

    def __estimate_fermi_energy__(self, v):
        try:
            Ef = brentq(self.integrated_charge, -self.Eg, self.Eg,
                        args=v, xtol=self.settings['fermi_solve_brentq_tol'])
        except (RuntimeError, RuntimeWarning, TypeError, ValueError) as e:
            traceback.print_exc()
            Ef = self.Eg / 2
        return Ef

    def rho_from_v(self, v):
        """Calculate the z-dependent fix and free charge density for a given v(z)."""
        rho_z = self.hole_density(v, self.Ef) - self.electron_density(v, self.Ef) \
                + self.total_charged_defect_density(v, self.Ef)
        return rho_z

    def rho_from_v_deriv(self, v):
        """Calculate the gradient of fix and free charge density for a given v(z)."""
        return self.hole_density_deriv(v, self.Ef) + self.electron_density_deriv(v, self.Ef) \
               + self.total_charged_defect_density_deriv(v, self.Ef)

    def integrated_charge(self, Ef, v):
        rho_z = self.hole_density(v, Ef) - self.electron_density(v, Ef) + self.total_charged_defect_density(v, Ef)
        extra_charge = 0.5 * (rho_z[0] * (np.abs(self.z_mesh[1] - self.z_mesh[0]))
                              + rho_z[-1] * (np.abs(self.z_mesh[-1] - self.z_mesh[-2])))
        # print('holes = ' + str(trapz(self.hole_density(v, Ef), self.z_mesh)) + ' extra charge = ' + str(extra_charge))
        return trapz(rho_z, self.z_mesh) + extra_charge - self.top_surface() - self.back_surface()

    def get_defect_densities(self, v, Ef, integrated=True):
        densities = {}
        for name, (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.donor_transitions.items():
            if name not in densities:
                densities[name] = density_array
            name = name + '+'
            if subband_width is None:
                densities[name] = np.multiply(density_array, expit(v - (Ef - transition_energy) / self.kT))
            else:
                densities[name] = np.multiply(density_array, spline((-(Ef - transition_energy) / self.kT) + v))

        for name, (transition_energy, density_array, idx_non_zero, subband_width, spline, spline_deriv) in self.acceptor_transitions.items():
            if name not in densities:
                densities[name] = density_array
            name = name + '-'
            if subband_width is None:
                densities[name] = np.multiply(density_array, expit(-v - (transition_energy - Ef) / self.kT))
            else:
                densities[name] = np.multiply(density_array, spline(((Ef - transition_energy) / self.kT) - v))

        if integrated:
            for name, density in densities.items():
                densities[name] = trapz(density, self.z_mesh)
        return densities
