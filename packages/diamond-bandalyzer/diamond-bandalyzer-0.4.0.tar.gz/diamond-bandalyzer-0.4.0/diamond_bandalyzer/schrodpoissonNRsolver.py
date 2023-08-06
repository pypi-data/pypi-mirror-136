__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import fdint

import diamond_bandalyzer.fundementalconstants as fc

from scipy.integrate import trapz
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.linalg import eigh_tridiagonal
from scipy.ndimage import gaussian_filter1d

from diamond_bandalyzer.poissonNRsolver import PoissonNRSolver
from diamond_bandalyzer.schrodpoissonequations import SchrodingerPoissonEquations
from diamond_bandalyzer.differentiationStencil import FourthOrderSecondDerivative
from diamond_bandalyzer.utilities import extrema_fast, normalise_inplace, inner_product
import diamond_bandalyzer.differentiationStencil as differentiationStencil
import matplotlib.pyplot as plt

class SchrodingerPoissonNRSolver(PoissonNRSolver):
    _settings_heading_ = "SchrodingerPoissonNRSolver"
    default_settings = {'derivativeorder': 4, 'numbasisvec': 10, 'has_back': False,
                        'numeigenstates': 5, 'useVxc': False}

    def __init__(self, z_mesh=None, init=None, ef_init=None, **kwargs):
        super().__init__(z_mesh, init=init, **kwargs)

        self.__add_default_settings__(SchrodingerPoissonNRSolver, **kwargs)

        self.omegaNR = self.settings['omega_nr_s']

        # ++ Constants ++ #
        self.has_back = self.settings['has_back']
        self.has_back = False
        self.num_basis = self.settings['numbasisvec']
        self.num_eigen_states = self.settings['numeigenstates']
        self.suppressor = 1
        if self.has_back:
            self.num_eigen_states = 2 * self.num_eigen_states

        self.useVxc = self.settings['useVxc']
        alpha = (4 / (9 * np.pi)) ** (1 / 3)
        dimlessRydberg = fc.e ** 2 / (8 * np.pi * fc.epsilon0 * fc.a0)
        self.XCconst = -(2 * fc.a0 * dimlessRydberg / (np.pi * alpha * self.settings['epsilond']))

        # ++ Variables ++ #
        self.holes = np.zeros(len(self.z_mesh))
        self.holes_deriv = np.zeros(len(self.z_mesh))
        self.vToPerturb = np.zeros(len(self.z_mesh))
        self.eigenFuncs = np.zeros((len(self.z_mesh), self.num_eigen_states, 3))
        self.eigenVals = np.zeros((self.num_eigen_states, 3))
        self.lancoz_coeff_a = np.longdouble(np.zeros((self.num_basis,)))
        self.lancoz_coeff_b = np.longdouble(np.zeros((self.num_basis-1,)))

        if not self.has_back:
            self.ddotStencil = FourthOrderSecondDerivative(self.z_mesh, sparse=True, zero_derivative_outside=False).get_stencil()
            self.lancoz_basis = np.zeros((self.num_basis + 1, len(self.z_mesh)), dtype=np.complex_)
            self.lancoz_basis[0] = self._initalise_lancoz_(self.z_mesh)
        else:
            pass


    def _initalise_lancoz_(self, z_mesh, guess='sin'):
        """Initialise the lancoz basis vectors, sets first vector by chosen guess, the rest are zero."""
        lancoz_initial = np.zeros(len(z_mesh), dtype=np.complex_)
        if guess == 'sin':
            lancoz_initial = np.sin(np.pi * z_mesh / z_mesh[-1], dtype=np.complex_) + 1j*np.sin(np.pi + np.pi * z_mesh / z_mesh[-1], dtype=np.complex_)
            lancoz_initial[0] = 0
            lancoz_initial[-1] = 0
        elif guess == 'triangle':
            midpoint = int(len(z_mesh)/2)
            lancoz_initial[:midpoint] = z_mesh[:midpoint]
            lancoz_initial[midpoint:] = z_mesh[-1] - z_mesh[midpoint:]
        else:
            lancoz_initial = gaussian_filter1d(np.random.random(len(z_mesh)), 10) + gaussian_filter1d(np.random.random(len(z_mesh)), 10) * 1j
        # not a typical normalisation.  Sqrt of <f0|f0>
        np.divide(lancoz_initial, np.sqrt(inner_product(lancoz_initial)), out=lancoz_initial)
        return lancoz_initial

    def hole_density(self, v, Ef, update=False):
        """ Computes the hole-gas spatial distribution from the quantum hole-gas model (Schrodinger-Poisson),
        if the potential has been changed but the wavefunctions have not been recomputed, the hole density is rescaled
        according to purtebation theory -> achieved by adding the change in potential to the F-D integrals."""

        self.holes.fill(0)
        deltaV = v - self.vToPerturb
        # TODO make this a sum-one-liner
        for subband in range(self.num_eigen_states):
            self.holes += self.eigenFuncs[:, subband, 0]*self.NVh * fdint.parabolic((-Ef + self.eigenVals[subband, 0]) / self.kT + deltaV) \
            + self.eigenFuncs[:, subband, 1]*self.NVl * fdint.parabolic((-Ef + self.eigenVals[subband, 1]) / self.kT + deltaV) \
            + self.eigenFuncs[:, subband, 2]*self.NVso * fdint.parabolic((-Ef - self.delSO + self.eigenVals[subband, 2]) / self.kT + deltaV)

        return self.holes

    def hole_density_deriv(self, v, Ef):
        """ Computes the hole density detivative, if the wavefunctions are not up to date with the potential the output
        is rescaled by peturbation theory."""

        self.holes_deriv.fill(0)
        delta_v = v - self.vToPerturb
        # TODO make this a sum-one-liner
        for subband in range(self.num_eigen_states):
            self.holes_deriv += self.NVh * self.eigenFuncs[:, subband, 0] * fdint.dparabolic(((-Ef + self.eigenVals[subband, 0]) / self.kT) + delta_v) \
            + self.NVl * self.eigenFuncs[:, subband, 1] * fdint.dparabolic(((-Ef + self.eigenVals[subband, 1]) / self.kT) + delta_v) \
            + self.NVso * self.eigenFuncs[:, subband, 2] * fdint.dparabolic(((-Ef - self.delSO + self.eigenVals[subband, 2]) / self.kT) + delta_v)
        return self.holes_deriv

    def __step__(self):
        """Does one step of the Newton-Raphson iteration"""
        #
        # Updating vTopPeturb is required when recaluating the holewavefucntions, move it to there.
        self.HoleWaveFunctions(self.holes, self.num_eigen_states, self.useVxc)


        # self.HoleWaveFunctions(None, None)
        super().__step__()

        # Recompute hole density for the exchange correlation potential if using quantum hole density
        self.hole_density(self.s_mesh, self.Ef)

    def __estimate_fermi_energy__(self, v):
        self.HoleWaveFunctions(self.holes, self.num_eigen_states, self.useVxc)
        return super().__estimate_fermi_energy__(v)

    def Hamiltonian(self, vOfZ, Vxc, m, wavefunction, backSurf=False, n=0):
        wavefunction[0] = 0
        wavefunction[-1] = 0
        func = wavefunction
        if not backSurf:
            ddot = self.ddotStencil.dot(wavefunction)
        else:
            ddot = self.ddotStencilBack.dot(wavefunction)
        ret = -(fc.h_bar ** 2 / (2 * m)) * ddot - vOfZ * func + func * Vxc  # [self.num_phantom:-self.num_phantom]*self.suppressor
        # plt.figure('H')
        # plt.plot(ret.real, label=str(n))
        # plt.figure('ddot')
        # # print(ddot)
        # plt.plot(-(fc.h_bar ** 2 / (2 * m))*ddot.real, label=str(n))
        # plt.xlim(0, 30)
        return ret

    def HoleWaveFunctions(self, holeDensity, Nstates, useVxc):
        zMesh = self.z_mesh
        np.copyto(self.vToPerturb, self.s_mesh)
        vOfZ = self.s_mesh*self.kT
        if self.has_back:
            wavefunctions = np.zeros((len(zMesh), Nstates, 3))  # Order is heavy, light, split-off
            holeDensityBack = holeDensity[self.midInd:]
            holeDensity = holeDensity[:self.midInd-1]
            zMeshBack = zMesh[self.midInd:]
            zMesh = zMesh[:self.midInd-1]
            guess = np.sin(np.pi*zMesh/zMesh[-1])
            guess = np.longdouble(guess/np.sqrt(trapz(np.multiply(np.conj(guess), guess), zMesh)))
            guessBack = np.sin(np.pi*zMeshBack/zMeshBack[-1])
            guessBack = np.longdouble(guessBack/np.sqrt(trapz(np.multiply(np.conj(guessBack), guessBack), zMeshBack)))
            vOfZBack = np.longdouble(vOfZ[self.midInd:])
            vOfZ = np.longdouble(vOfZ[:self.midInd-1])

        energies = np.zeros((Nstates, 3))
        masses = np.array([self.mhh, self.mhl, self.mso])
        #Do this for all three sub-bands
        for i in range(3):
            if not self.has_back:
                energies[:, i] = self.Lanczos(zMesh, self.z_mesh, vOfZ, holeDensity, self.eigenFuncs[:, :, i], Nstates, masses[i], False, useVxc)

            else:
                halfway = np.int(Nstates/2)
                wavefunctions[:self.midInd-1, :halfway, i], energies[:halfway, i] = self.Lanczos(zMesh, vOfZ, holeDensity, self.eigenFuncs[:, :, i], Nstates, masses[i], False, useVxc)
                wavefunctions[self.midInd:, halfway:, i], energies[halfway:, i] = self.Lanczos(zMesh, vOfZ, holeDensity, self.eigenFuncs[:, :, i], Nstates, masses[i], False, useVxc)
        # self.eigenFuncs = wavefunctions.real
        self.eigenVals = -1*energies # easier to keep track of this minus sign here rather than in hole density function
        return

    def Lanczos(self, z_mesh, z_mesh_phantom, vOfZ, holeDensity, eigenfuncs, Nstates, mass, backSurf, useVxc):
        if useVxc:
            Vxc = self.exchangeCorr(mass, np.longdouble(holeDensity))
        else:
            Vxc = 0

        # plt.figure('H')
        # plt.clf()
        # plt.figure('ddot')
        # plt.clf()
        a = self.lancoz_coeff_a
        b = self.lancoz_coeff_b
        self.lancoz_basis[1] = self.Hamiltonian(vOfZ, Vxc, mass, self.lancoz_basis[0], backSurf)
        a[0] = inner_product(self.lancoz_basis[0], b=self.lancoz_basis[1], x=z_mesh_phantom)
        self.lancoz_basis[1] -= a[0] * self.lancoz_basis[0]
        for i in range(1, self.num_basis):
            b[i-1] = np.sqrt(inner_product(self.lancoz_basis[i], x=z_mesh_phantom))
            np.divide(self.lancoz_basis[i], b[i - 1], out=self.lancoz_basis[i])
            self.lancoz_basis[i + 1] = self.Hamiltonian(vOfZ, Vxc, mass, self.lancoz_basis[i], backSurf, n=i)
            a[i] = inner_product(self.lancoz_basis[i], b=self.lancoz_basis[i + 1], x=z_mesh_phantom)
            self.lancoz_basis[i + 1] -= a[i] * self.lancoz_basis[i] + b[i - 1] * self.lancoz_basis[i - 1]

        # plt.figure('H')
        # plt.legend()
        # plt.figure('ddot')
        # plt.legend()
        # input()
        energies, vectors = eigsh(sparse.diags((b, a, b), offsets=(-1, 0, 1), dtype=np.double), k=Nstates, which='SA', return_eigenvectors=True)
        rebasis_eigenfunctions = np.dot(vectors.T, self.lancoz_basis[:-1])
        rebasis_eigenfunctions = np.multiply(np.conj(rebasis_eigenfunctions), rebasis_eigenfunctions).T
        rebasis_eigenfunctions = np.divide(rebasis_eigenfunctions, trapz(rebasis_eigenfunctions, x=z_mesh, axis=0))
        np.copyto(eigenfuncs, rebasis_eigenfunctions.real)
        return energies

    def exchangeCorr(self, m, holeDensity):
        astar = 4 * np.pi * self.settings['epsilond'] * fc.epsilon0 * fc.h_bar**2 / (m * fc.e * fc.e)
        Vxc = self.kT * self.XCconst * (np.power((4 / 3) * np.pi * holeDensity, 1 / 3) + (0.7734 / (21 * astar)) * np.log(
            1 + 21 * astar * np.power((4 / 3) * np.pi * holeDensity, 1 / 3)))
        return Vxc

    def __updates__(self, n):
        super().__updates__(n)
        # if self.diff < 1e-3*self.omegaNR:
        #     self.suppressor = 1

    # def __update_end_condition__(self):
    #     pass
