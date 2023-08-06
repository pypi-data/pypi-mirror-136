"""Derived class that solves the Poisson equation for a diamond by Newton-Rhapson minimisation."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import math
from scipy import sparse
from scipy.integrate import trapz
from scipy.optimize import line_search
from diamond_bandalyzer.solver import Solver
from diamond_bandalyzer.poissonequations import PoissonEquations
from diamond_bandalyzer.utilities import extrema_fast
from scipy.optimize import line_search
import diamond_bandalyzer.differentiationStencil as differentiationStencil
import matplotlib.pyplot as plt


class PoissonNRSolver(Solver, PoissonEquations):
    _settings_heading_ = "PoissonNRSolver"
    default_settings = {'derivative_order': 4, 'omega_nr': 0.5, 'omega_nr_min': 0, 'omega_nr_max': 1,
                        'wolfe_c1': 0.0001, 'wolfe_c2': 0.99, 'ratio_of_convergence': 0.2, 'extra_phantom_pts': 10}

    def __init__(self, z_mesh=None, init=None, **kwargs):
        super().__init__(z_mesh, init=init, **kwargs)
        self.__add_default_settings__(PoissonNRSolver, **kwargs)

        self.Ef = 0
        self.Ef_backup = self.Ef
        self.diff = 1e6
        self.z_mesh = z_mesh
        self.z_mesh_diffs = np.diff(self.z_mesh)
        self.order = self.settings['derivative_order']
        self.num_phantom = int(self.order + self.settings['extra_phantom_pts'])
        self.omegaNR = self.settings['omega_nr']
        self.line_search_flag = False

        # TODO move into solver initalise.
        if self.order == 2 or self.order == 4:  # Phantom point initialization stuff
            self.z_mesh_phantom = np.zeros(len(self.z_mesh) + 2 * self.num_phantom)
            self.s_mesh_phantom = np.zeros(len(self.s_mesh) + 2 * self.num_phantom)
            self.z_mesh_phantom[self.num_phantom:-self.num_phantom] = self.z_mesh
            self.z_mesh_phantom[0:self.num_phantom] = self.z_mesh[0] + np.arange(-self.num_phantom, 0, 1) * \
                                                      self.z_mesh_diffs[0]
            self.z_mesh_phantom[-self.num_phantom:] = self.z_mesh[-1] + np.arange(1, self.num_phantom + 1, 1) * \
                                                      self.z_mesh_diffs[-1]
            self.z_mesh_phantom_diffs = np.diff(self.z_mesh_phantom)
            self.z_mesh = self.z_mesh_phantom[self.num_phantom:-self.num_phantom]
            self.s_mesh_phantom[self.num_phantom:-self.num_phantom] = self.s_mesh
            self.s_mesh_last_phantom = np.zeros((len(self.s_mesh_phantom)))
            self.s_mesh = self.s_mesh_phantom[self.num_phantom:-self.num_phantom]
            if self.order == 2:
                self.stencil = differentiationStencil.SecondOrderSecondDerivative(self.z_mesh_phantom,
                                                                                  self.z_mesh_phantom_diffs,
                                                                                  sparse=True,
                                                                                  zero_derivative_outside=True)
            elif self.order == 4:
                # self.stencil = differentiationStencil.FourthOrderSecondDerivative(self.z_mesh_phantom,
                #                                                                   self.z_mesh_phantom_diffs)

                self.stencil = differentiationStencil.FourthOrderSecondDerivative(self.z_mesh_phantom,
                                                                                  self.z_mesh_phantom_diffs,
                                                                                  sparse=True,
                                                                                  zero_derivative_outside=True)
        else:
            raise NotImplementedError('We only have 2nd and 4th order accurate 2nd derivatives!')

        # TODO check what we need to keep in persistent memory.
        self.ddot_stencil = self.stencil.get_stencil()
        self.lhs_stencil = sparse.csr_matrix(self.ddot_stencil, copy=True)
        # self.stencil.modifyEndPoints()
        # self.ddot_stencil = sparse.csr_matrix(self.stencil.get_stencil())
        # self.lhs_stencil = sparse.csr_matrix(self.stencil.get_stencil())

        self.original_diagonal = self.ddot_stencil.diagonal(0)
        self.charge_deriv_terms = np.zeros(len(self.z_mesh_phantom))

    def __step__(self):
        """Does one step of the Newton-Raphson iteration"""
        # input()
        rhs = self.generate_rhs(self.s_mesh_phantom)  # RHS of the equation
        lhs_stencil = self.generate_lhs(self.s_mesh_phantom)  # LHS (matrix) of the equation
        step_direc = sparse.linalg.spsolve(lhs_stencil, -rhs, use_umfpack=True)  # Solve for the next step

        # If required to an inexact line-search to determine suitable omega before taking the step. Helps stability.
        if self.line_search_flag:
            # Do line search here
            oldfprime = self.fprime(self.s_mesh_phantom)
            oldf = self.f(self.s_mesh_phantom)
            oldoldf = self.f(self.s_mesh_last_phantom)

            try:
                searchResults = line_search(self.f, self.fprime, self.s_mesh_phantom, step_direc, oldfprime, oldf,
                                            oldoldf, c1=self.settings['wolfe_c1'], c2=self.settings['wolfe_c2'],
                                            maxiter=1000)
                if searchResults[0] is not None:
                    if searchResults[0] > self.settings['omega_nr_min']:
                        if searchResults[0] < self.settings['omega_nr_max']:
                            self.omegaNR = searchResults[0]
                        else:
                            self.omegaNR = self.settings['omega_nr_max']
                    else:
                        self.omegaNR = self.settings['omega_nr_min']
                else:
                    pass
            except:
                print("LS failed")
                self.omegaNR = 0.9 * self.omegaNR

        # Take the omega scaled step
        np.copyto(self.s_mesh_last_phantom, self.s_mesh_phantom)
        self.s_mesh_phantom = np.add(self.s_mesh_phantom, self.omegaNR * step_direc, out=self.s_mesh_phantom)

    #  print(self.z_mesh[-1])

    def _initialise_solver_(self):
        self.Ef = self.__estimate_fermi_energy__(self.s_mesh)
        if self.from_inital_soln:
            # ensure phantom points are zero:
            np.put(self.s_mesh_phantom, range(-self.num_phantom, self.num_phantom), 0.)
            for i in range(self.num_phantom):
                F = self.generate_rhs(self.s_mesh_phantom)
                lii = self.num_phantom - 1 - i  # location of last leading phantom point
                ljj = lii + int(self.order / 2)  # location of F that solves for lii.
                tii = -self.num_phantom + i  # location of first trailing phantom point
                tjj = tii - int(self.order / 2)
                self.s_mesh_phantom[lii] = -F[ljj] / self.ddot_stencil[ljj, lii]  # Calc value of lii from F
                self.s_mesh_phantom[tii] = -F[tjj] / self.ddot_stencil[tjj, tii]

            f_diverge = False
            f_diverge_val = 0
            b_diverge = False
            b_diverge_val = 0
            for i in range(self.num_phantom):  # use the step difference to estimate the rest of the phantom points.
                lii = self.num_phantom - i - 1
                if f_diverge:
                    self.s_mesh_phantom[lii] = f_diverge_val
                elif lii > 0:
                    if math.fabs(self.s_mesh_phantom[lii - 1] - self.s_mesh_phantom[lii]) > \
                            math.fabs(self.s_mesh_phantom[lii] - self.s_mesh_phantom[lii + 1]):
                        f_diverge = True
                        f_diverge_val = self.s_mesh_phantom[lii]

                tii = -self.num_phantom + i
                if b_diverge:
                    self.s_mesh_phantom[tii] = b_diverge_val
                elif tii < -1:
                    if math.fabs(self.s_mesh_phantom[tii - 1] - self.s_mesh_phantom[tii]) < \
                            math.fabs(self.s_mesh_phantom[tii] - self.s_mesh_phantom[tii + 1]):
                        b_diverge = True
                        b_diverge_val = self.s_mesh_phantom[tii]
            self.omegaNR = 3e-4
            self.__updates__(-1)

    def f(self, x):
        g = self.generate_rhs(x)
        #  g = np.multiply(g, np.concatenate((self.z_mesh_phantom_diffs, [self.z_mesh_phantom_diffs[-1]])))
        #  print(np.matmul(np.transpose(g), g))
        return np.matmul(np.transpose(g), g)

    def fprime(self, x):
        g = self.generate_rhs(x)
        #  g = np.multiply(g, np.concatenate((self.z_mesh_phantom_diffs, [self.z_mesh_phantom_diffs[-1]])))
        dg = self.generate_lhs(x)
        #  print(2*np.transpose(dg).dot(g))
        return 2 * np.transpose(dg).dot(g)

    def wolfe_upper(self, omega, oldF, step_direc, step_direc_grad_f, plot=False):
        """Returns the ratio of z_mesh points that exceed the wolfe upper bound"""
        line_search = omega * self.settings['wolfe_c1'] * step_direc_grad_f
        new_mesh = np.add(self.s_mesh_phantom, self.omegaNR * step_direc)
        newF = self.generate_rhs(new_mesh)
        return trapz(np.abs(newF), self.z_mesh_phantom) \
               - trapz(np.abs(oldF + line_search), self.z_mesh_phantom)

    def wolfe_lower(self, omega, step_direc, step_direc_grad_f):
        """Returns the ratio of z_mesh points that don't meet the wolfe lower bound"""
        new_mesh = np.add(self.s_mesh_phantom, omega * step_direc)
        lhs_stencil = self.generate_lhs(new_mesh)
        return trapz(np.abs(np.transpose(lhs_stencil).dot(step_direc)), self.z_mesh_phantom) - self.settings['wolfe_c2'] \
               * trapz(np.abs(step_direc_grad_f), self.z_mesh_phantom)

    def __updates__(self, n):
        super().__updates__(n)
        # allow line searching after a certain tolerance is met.
        if self.diff < 1e3 / self.omegaNR:
            self.line_search_flag = True
        # If close to convergence, shift the solution (and Ef) so that the minimum potential is 0
        if self.diff < (1 / self.omegaNR):
            self.EfOld = self.Ef
            minVal = np.min(self.s_mesh)
            self.Ef = self.Ef - self.kT * minVal
            self.s_mesh_phantom -= minVal
            self.s_mesh_last -= minVal
            self.s_mesh_last_phantom -= minVal

    def __updated_end_condition__(self):
        return self.end_condition * self.omegaNR

    def generate_rhs(self, s_mesh_phantom):
        s_mesh = s_mesh_phantom[self.num_phantom:-self.num_phantom]
        rhs = self.ddot_stencil.dot(s_mesh_phantom)  # Laplacian of v
        rhs[self.num_phantom:-self.num_phantom] += self.constRhotoV * self.rho_from_v(
            s_mesh)  # Add scaled charge density

        rhs[self.num_phantom] -= self.constRhotoV * self.top_surface() / \
                                     self.z_mesh_phantom_diffs[0]  # Top surface charge density

        rhs[-self.num_phantom-1] -= self.constRhotoV * self.back_surface() / \
                                  self.z_mesh_phantom_diffs[-1]  # Back surface charge density
        return rhs

    def generate_lhs(self, s_mesh_phantom):
        s_mesh = s_mesh_phantom[self.num_phantom:-self.num_phantom]
        # Sum the total derivative of all bulk charges (electrons, holes, defects)
        self.charge_deriv_terms.fill(0)
        self.charge_deriv_terms[self.num_phantom:-self.num_phantom] = self.rho_from_v_deriv(s_mesh)
        # Create the LHS of the equation to be solved by changing the 3 central diagonals
        lhs_stencil = self.lhs_stencil
        lhs_stencil.setdiag(self.original_diagonal + self.constRhotoV * self.charge_deriv_terms)

        return lhs_stencil

    # def setup_progress_bar(self):
    #     postfix = {'omega': self.omegaNR}
    #     super().setup_progress_bar(postfix)

    def update_progress_bar(self, x=None, postfix={}):
        x = self.diff / self.omegaNR
        postfix = {'omega': self.omegaNR}
        super().update_progress_bar(x, postfix)
    #
    # def __update_end_condition__(self):
    #     pass
