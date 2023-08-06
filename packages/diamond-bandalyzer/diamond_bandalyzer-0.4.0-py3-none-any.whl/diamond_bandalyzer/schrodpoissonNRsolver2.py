__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import fdint

import diamond_bandalyzer.fundementalconstants as fc

from scipy.integrate import trapz
from scipy import sparse
from scipy.sparse.linalg import eigsh

from diamond_bandalyzer.poissonNRsolver import PoissonNRSolver
from diamond_bandalyzer.schrodpoissonequations import SchrodingerPoissonEquations
from diamond_bandalyzer.differentiationStencil import FourthOrderSecondDerivative
from diamond_bandalyzer.utilities import extrema_fast, normalise_inplace, inner_product

import matplotlib.pyplot as plt

class SchrodingerPoissonNRSolver(PoissonNRSolver):  # SchrodingerPoissonEquations  - we ignore this for a bit
    _settings_heading_ = "SchrodingerPoissonNRSolver"
    default_settings = {'derivativeorder': 4, 'numbasisvec': 10, 'has_back': False,
                        'numeigenstates': 5, 'useVxc': False}

    def __init__(self, z_mesh=None, init=None, ef_init=None, **kwargs):
        super().__init__(z_mesh, init=init, **kwargs)
        self.__add_default_settings__(SchrodingerPoissonNRSolver, **kwargs)

        # ++ Constants ++ #
        self.has_back = False # self.settings['has_back']
        self.num_basis = self.settings['numbasisvec']
        self.num_eigen_states = self.settings['numeigenstates']
        if self.has_back:
            self.num_eigen_states = 2 * self.num_eigen_states
        self.useVxc = self.settings['useVxc']

        # ++ Variables ++ #
        self.v_to_perturb = np.zeros(len(self.z_mesh))
        self.delta_v = np.zeros(len(self.z_mesh))
        self.holes = np.zeros(len(self.z_mesh))
        self.holes_deriv = np.zeros(len(self.z_mesh))
        self.eigenFuncs = np.zeros((len(self.z_mesh), self.num_eigen_states, 3))
        self.eigenVals = np.zeros((self.num_eigen_states, 3))

        # TODO Are these used?
        self.a = fc.a0  # Bohr radius
        alpha = (4 / (9 * np.pi)) ** (1 / 3)
        dimlessRydberg = fc.e * fc.e / (8 * np.pi * fc.epsilon0 * self.a)
        self.XCconst = -(2 * self.a * dimlessRydberg / (np.pi * alpha * self.settings['epsilond']))

        self.ddotStencilBack = None
        self.guess_back = None
        if not self.has_back:
            self.ddotStencil = FourthOrderSecondDerivative(self.z_mesh, sparse=True).get_stencil()
            self.lancoz_basis = self._initalise_lancoz_(self.z_mesh, self.num_basis)
        else:
            # TODO initialisation for lancoz basis and stencil for both surfaces.
            raise NotImplementedError("Can't deal with your backsurface yet mate")


    def _initalise_lancoz_(self, z_mesh, num_basis_vectors, guess='sin'):
        """Initialise the lancoz basis vectors, sets first vector by chosen guess, the rest are zero."""
        lancoz_basis = np.zeros((self.num_basis + 1, len(z_mesh)), dtype=np.complex_)
        if guess == 'sin':
            lancoz_basis[0] = np.sin(np.pi * z_mesh / z_mesh[-1], dtype=np.complex_)
        else:
            lancoz_basis[0] = np.random.random(len(z_mesh)) + np.random.random(len(z_mesh)) * 1j
        # not a typical normalisation.  Sqrt of <f0|f0>
        np.divide(lancoz_basis[0], np.sqrt(inner_product(lancoz_basis[0])), out=lancoz_basis[0])
        return lancoz_basis

    def __step__(self):
        """Does one step of the Newton-Raphson iteration, updates s_mesh and s_mesh last."""
        super().__step__()
        self.HoleWaveFunctions(None, None)
        # Recompute hole density for the exchange correlation potential if using quantum hole density
        # self.hole_density(self.s_mesh, self.Ef)
        # self.diff = np.max(np.abs(extrema_fast(self.s_mesh - self.s_mesh_last)))

        # TODO: Recompute wavefunctions (the corrector) using the hole densities associated with the updated V (the predictor)
    def __updates__(self, n):
        # self.hole_density(self.s_mesh, self.Ef, update=True)
        # self.HoleWaveFunctions(self.kT * self.s_mesh, self.holes)
        super().__updates__(n)

    def generate_rhs(self, s_mesh_phantom):
        s_mesh = s_mesh_phantom[self.num_phantom:-self.num_phantom]
        rhs = self.ddot_stencil.dot(s_mesh_phantom)  # Laplacian of v
        rhs[self.num_phantom:-self.num_phantom] += self.constRhotoV * self.rho_from_v(
            s_mesh, True)  # Add scaled charge density

        rhs[self.num_phantom - 1] -= self.constRhotoV * self.top_surface(self.Ef, s_mesh[0]) / \
                                     self.z_mesh_phantom_diffs[0]  # Top surface charge density

        rhs[-self.num_phantom] -= self.constRhotoV * self.back_surface(self.Ef, s_mesh[-1]) / \
                                  self.z_mesh_phantom_diffs[-1]  # Back surface charge density
        return rhs

    def rho_from_v(self, v, update=False):
        """Calculate the z-dependent fix and free charge density for a given v(z)."""
        rho_z = self.hole_density(v, self.Ef, update=update) - self.electron_density(v, self.Ef) \
                + self.total_charged_defect_density(v, self.Ef)
        return rho_z

    # override the hole denstiy calculation to be semi-quantum.
    def hole_density(self, v, Ef, update=False):
        """ Computes the hole-gas spatial distribution. The update flag sets if the wavefunctions are recomputed before
        determining the hole density. If they are not recomputed, the hole density is simply rescaled according to the
        change in potential by adding the change in potential to the F-D integrals."""
        # if update:
        #     # recompute eigenfunctions and eigenvalues
        #     # print('This', type(self.vToPerturb), type(v))
        #
        #     self.HoleWaveFunctions(self.kT * v, self.holes)
        #     self.holes.fill(0)
        #     for sub_band in range(self.num_eigen_states):
        #         self.holes += self.NVh * self.eigenFuncs[:, sub_band, 0] * fdint.parabolic((-Ef + self.eigenVals[sub_band, 0]) / self.kT)
        #         # self.holes += self.NVl * self.eigenFuncs[:, sub_band, 1] * fdint.parabolic((-Ef + self.eigenVals[sub_band, 1]) / self.kT)
        #         # self.holes += self.NVso * self.eigenFuncs[:, sub_band, 2] * fdint.parabolic((-Ef - self.delSO + self.eigenVals[sub_band, 2]) / self.kT)
        # else:
        delta_v = v - self.v_to_perturb
        self.holes.fill(0)
        for sub_band in range(self.num_eigen_states):
            self.holes += self.NVh * self.eigenFuncs[:, sub_band, 0] * fdint.parabolic(((-Ef + self.eigenVals[sub_band, 0]) / self.kT) + delta_v)
            # self.holes += self.NVl * self.eigenFuncs[:, sub_band, 1] * fdint.parabolic(((-Ef + self.eigenVals[sub_band, 1]) / self.kT) + self.delta_v)
            # self.holes += self.NVso * self.eigenFuncs[:, sub_band, 2] * fdint.parabolic(((-Ef - self.delSO + self.eigenVals[sub_band, 2]) / self.kT) + self.delta_v)

        return self.holes

    def hole_density_deriv(self, v, Ef):
        self.holes_deriv.fill(0)
        delta_v = v - self.v_to_perturb
        for subband in range(self.num_eigen_states):
            self.holes_deriv += self.NVh * self.eigenFuncs[:, subband, 0] * fdint.dparabolic(((-Ef + self.eigenVals[subband, 0]) / self.kT) + delta_v)
            # self.holes_deriv += self.NVl * self.eigenFuncs[:, subband, 1] * fdint.dparabolic(((-Ef + self.eigenVals[subband, 1]) / self.kT) + self.delta_v)
            # self.holes_deriv += self.NVso * self.eigenFuncs[:, subband, 2] * fdint.dparabolic(((-Ef - self.delSO + self.eigenVals[subband, 2]) / self.kT) + self.delta_v)
        return self.holes_deriv

    def HoleWaveFunctions(self, vOfZ, holeDensity):
        np.copyto(self.v_to_perturb, self.s_mesh)
        self.eigenFuncs.fill(0)
        if self.has_back:
            holeDensityBack = holeDensity[self.midInd:]
            holeDensity = holeDensity[:self.midInd - 1]
            zMeshBack = self.z_mesh[self.midInd:]
            zMesh = self.z_mesh[:self.midInd - 1]
            vOfZBack = vOfZ[self.midInd:]
            vOfZ = vOfZ[:self.midInd - 1]

        energies = np.zeros((self.num_eigen_states, 3))
        masses = np.array([self.mhh, self.mhl, self.mso])
        # Do this for all three sub-bands
        for i in range(3):
            if not self.has_back:
                energies[:, i] = self.Lanczos(self.z_mesh, self.eigenFuncs[:, :, i], self.s_mesh*self.kT, self.holes,
                                              self.num_eigen_states, masses[i], False)
            else:
                halfway = np.int(self.num_eigen_states / 2)
                energies[:halfway, i] = self.Lanczos(zMesh, self.eigenFuncs[:self.midInd - 1, :halfway, i],
                                                     vOfZ, holeDensity, self.guess, halfway, masses[i], False)
                energies[halfway:, i] = self.Lanczos(zMeshBack, self.eigenFuncs[self.midInd:, halfway:, i],
                                                     vOfZBack, holeDensityBack, self.guess_back, halfway, masses[i], True)

        self.eigenVals = -1 * energies  # easier to keep track of this minus sign here rather than in hole density function
        return

    def Hamiltonian(self, vOfZ, Vxc, m, func, backSurf=False):
        func[0] = 0
        func[-1] = 0
        if not backSurf:
            ddot = self.ddotStencil.dot(func)
        else:
            ddot = self.ddotStencilBack.dot(func)
        return -(fc.h_bar ** 2 / (2 * m)) * ddot - vOfZ * func + func * Vxc


    def exchangeCorr(self, m, holeDensity):
        # TODO : make this value of self.a (bohr raidus)
        astar = 4 * np.pi * self.settings['epsilond'] * fc.epsilon0 * fc.h_bar ** 2 / (m * fc.e * fc.e)
        # TODO : clean up hardcoded constants
        Vxc = self.kT * self.XCconst * (
                np.power((4 / 3) * np.pi * holeDensity, 1 / 3) + (0.7734 / (21 * astar)) * np.log(
            1 + 21 * astar * np.power((4 / 3) * np.pi * holeDensity, 1 / 3)))
        return Vxc

    def Lanczos(self, zMesh, eigen_functions, vOfZ, holeDensity, num_eigen_states, mass, backSurf):
        if self.useVxc:
            Vxc = self.exchangeCorr(mass, np.longdouble(holeDensity))
        else:
            pass
        Vxc = 0

        #  These are the ortho-normalisation coefficients for generating the lancoz basis, they also form hamiltonian
        #  eigenvalues for the lancoz basis based on how they are generated.
        a = np.zeros(self.num_basis)
        b = np.zeros(self.num_basis - 1)

        # Calculate the lancoz basis via the Ojalvo-Newmann method
        self.lancoz_basis[1] = self.Hamiltonian(vOfZ, Vxc, mass, self.lancoz_basis[0], backSurf)
        a[0] = inner_product(self.lancoz_basis[0], b=self.lancoz_basis[1], x=zMesh)
        self.lancoz_basis[1] -= a[0] * self.lancoz_basis[0]
        for i in range(1, self.num_basis):
            b[i-1] = np.sqrt(inner_product(self.lancoz_basis[i], x=zMesh))
            np.divide(self.lancoz_basis[i], b[i-1], out=self.lancoz_basis[i])
            self.lancoz_basis[i+1] = self.Hamiltonian(vOfZ, Vxc, mass, self.lancoz_basis[i], backSurf)
            a[i] = inner_product(self.lancoz_basis[i], b=self.lancoz_basis[i+1], x=zMesh)
            self.lancoz_basis[i+1] -= a[i] * self.lancoz_basis[i] + b[i-1]*self.lancoz_basis[i-1]

        # a and b guaranteed real positive, they are used to form a real symmetric tri-diagonal hamiltonian
        reduced_hamiltonian = sparse.diags((b, a, b), offsets=(-1, 0, 1), dtype=np.double)
        # print('Reduced_hamiltonian', reduced_hamiltonian)
        energies, vectors = eigsh(reduced_hamiltonian, k=num_eigen_states, which='SA', return_eigenvectors=True)
        # print(self.Ef, energies, vectors)
        for i in range(num_eigen_states):
            temp = np.zeros(len(eigen_functions[:, i]), dtype=np.complex_)
            for j in range(self.num_basis):
                np.add(temp, vectors[j, i] * self.lancoz_basis[j, :], out=temp)
            eigen_functions[:, i] = np.abs(temp)
            np.multiply(np.conj(temp), temp, out=temp)
            np.divide(temp.real, trapz(temp.real, x=zMesh), out=eigen_functions[:, i])
        # plt.figure('tester')
        # plt.clf()
        # plt.plot(eigen_functions)
        return energies

    def __estimate_fermi_energy__(self, v):
        self.HoleWaveFunctions(self.kT * v, np.zeros(len(self.z_mesh)))
        return super().__estimate_fermi_energy__(v)
