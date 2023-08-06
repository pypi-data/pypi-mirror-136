"""Derived class that solves the Poisson equation for a diamond by relaxtion."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import diamond_bandalyzer.fundementalconstants as fc
from diamond_bandalyzer.solver import Solver
from diamond_bandalyzer.poissonequations import PoissonEquations
from diamond_bandalyzer.utilities import extrema_fast


class PoissonRelaxationSolver(Solver, PoissonEquations):
    _settings_heading_ = "PoissonRelaxationSolver"
    default_settings = {'omega_min': 5e-7, 'omega_max': 1e-1, 'omega_inital': 1e-5}

    # TODO: check if our 'simplified' solution condition is sufficient.  Dan has made provisions for testing Ef and
    # TODO: acceptor density changes.
    # 'atol_Ef': 1e-8, 'rtol_defect': 1e-7,

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__add_default_settings__(PoissonRelaxationSolver, **kwargs)
        self.omega = self.settings['omega_inital']
        self.omegaMax = self.settings['omega_max']
        self.omegaMin = self.settings['omega_min']

        self.s_mesh_backup = np.copy(self.s_mesh)
        self.Ef = self.__estimate_fermi_energy__(self.s_mesh)
        self.Ef_backup = self.Ef
        self.old_diff_ratio = 0
        self.future_diff = 1e10
        self.criticalFlag = False  # flag set to indicate if solver diverging.

    def __step__(self):
        """Does one relaxation pass of the band-bending, omega is the successive over-relaxation parameter used to speed
        convergence (see "Iterative Solution of Large Linear Systems" by David M. Young, Jr (1971))
        beta is a 'trajectory' parameter used to move the solution in the correct direction by scaling the difference
        between the n and (n-1)th iterations and adding this to the next iteration"""
        old_future_diff = self.future_diff
        rho = self.rho_from_v(self.s_mesh)
        e_field = self.e_field_from_rho(rho, self.s_mesh[0], self.s_mesh[-1])
        single_step = self.v_from_e_field(e_field)
        rk4_step = self.pseudoRK4(self.omega)
        self.future_diff = np.max(np.abs(extrema_fast(rk4_step - single_step)))
        diff_ratio = self.future_diff / old_future_diff

        # Solution diverging wildly - return to a backup - cross your fingers.
        if diff_ratio > 100:
            if self.criticalFlag:  # Unsalvageable - this solution has failed.
                self.__fail_solver__("Relaxation solution has diverged and could not be recovered by slower solving from"
                                     "backup, dumping current state as solution.  Something has gone horribly wrong.")
            else:
                print("Diverging!!!")
                np.copyto(self.s_mesh, self.s_mesh_backup)
                self.omega = self.omegaMin
                self.Ef = self.Ef_backup
                self.criticalFlag = True  # don't try to run from backup twice.

        # Emergency proportional feedback control - DO NOT TAKE THE STEP AS-IS!!!
        elif diff_ratio > 10:
            print("Almost Diverging :S")
            self.omega = 0.8 * self.omega
            vOfZtest = np.multiply((1 - self.omega), self.s_mesh) + np.multiply(self.omega, single_step)
            self.s_mesh = vOfZtest - np.min(vOfZtest)

        # Normal derivative feedback control, manually tuned.
        else:
            if diff_ratio > 3:
                if self.diff > 1:
                    self.omega = 0.9 * self.omega
                elif self.diff < 1:
                    if self.diff < 1e-5:
                        self.omega = 0.999 * self.omega
                    else:
                        self.omega = 0.99 * self.omega
            else:
                if np.sign(diff_ratio - 1) != np.sign(self.old_diff_ratio - 1):
                    if self.diff < 1e-5:
                        self.omega = 0.999 * self.omega
                    else:
                        self.omega = 0.99 * self.omega
                elif self.diff > 1/self.kT:
                    #           if ratio < 1:
                    self.omega = 1.001 * self.omega
                elif self.diff < 1/self.kT:
                    self.omega = 1.0001 * self.omega
            self.s_mesh = rk4_step - np.min(rk4_step)
        if self.omega > self.omegaMax:
            self.omega = self.omegaMax
        elif self.omega < self.omegaMin:
            self.omega = self.omegaMin
        self.old_diff_ratio = diff_ratio

    def pseudoRK4(self, omega):
        # More stable version of the naive iteration. Allows bigger omega.
        F1 = self.v_from_e_field(self.e_field_from_rho(self.rho_from_v(self.s_mesh), self.s_mesh[0], self.s_mesh[-1]))
        temp = (1 - (omega / 2)) * self.s_mesh + omega * F1 / 2
        F2 = self.v_from_e_field(self.e_field_from_rho(self.rho_from_v(temp), temp[0], temp[-1]))
        temp = (1 - (omega / 2)) * self.s_mesh + omega * F2 / 2
        F3 = self.v_from_e_field(self.e_field_from_rho(self.rho_from_v(temp), temp[0], temp[-1]))
        temp = (1 - omega) * self.s_mesh + omega * F3
        F4 = self.v_from_e_field(self.e_field_from_rho(self.rho_from_v(temp), temp[0], temp[-1]))

        vNext = (1 / 6) * (6 * self.s_mesh - omega * (6 * self.s_mesh - F1 - F2 - F3 - F4))
        return vNext - np.min(vNext)

    def __updates__(self, n):
        if np.mod(n, 1000) == 0:
            np.copyto(self.s_mesh_backup, self.s_mesh)
            self.Ef_backup = self.Ef
            self.criticalFlag = False

        self.update_fermi_energy(self.s_mesh)
