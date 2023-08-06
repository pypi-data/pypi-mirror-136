import numpy as np
import diamond_bandalyzer.fundementalconstants as fc
from scipy.integrate import cumtrapz, trapz
import fdint
from scipy.special import expit
from scipy import sparse
from scipy.sparse.linalg import eigsh
from diamond_bandalyzer.poissonequations import PoissonEquations
from scipy.optimize import brentq
import traceback
import bisect
from diamond_bandalyzer.defects import Defects
import diamond_bandalyzer.differentiationStencil as differentiationStencil


class SchrodingerPoissonEquations(PoissonEquations):
    _settings_heading_ = "SchrodingerPoissonEquations"
    default_settings = {'numbasisvec': 10, 'has_back': False,
                        'numeigenstates': 5, 'useVxc': False}

    def __init__(self, z_mesh=None, **kwargs):
        super().__init__(z_mesh=z_mesh, **kwargs)
        self.__add_default_settings__(SchrodingerPoissonEquations, **kwargs)
        # ++ Arguments ++ #
        if not hasattr(self, 'z_mesh'):  # might already have this from multiple inheritance with a solver.
            self.z_mesh = z_mesh

        # ++ Constants ++ #
        self.h_bar = fc.h / (2 * np.pi)
        self.has_back = self.settings['has_back']
        self.has_back = False
        self.num_basis = self.settings['numbasisvec']
        self.num_eigen_states = self.settings['numeigenstates']
        if self.has_back:
            self.num_eigen_states = 2 * self.num_eigen_states
        self.useVxc = self.settings['useVxc']

        # ++ Variables ++ #

        self.holeDensity = np.zeros(len(self.z_mesh))
        self.eigenFuncs = np.zeros((len(self.z_mesh), self.num_eigen_states, 3))
        self.eigenVals = np.zeros((self.num_eigen_states, 3))
        self.a = 4 * np.pi * fc.epsilon0 * self.h_bar * self.h_bar / (fc.mo * fc.e * fc.e)  # Bohr radius
        alpha = (4 / (9 * np.pi)) ** (1 / 3)
        dimlessRydberg = fc.e * fc.e / (8 * np.pi * fc.epsilon0 * self.a)
        self.XCconst = -(2 * self.a * dimlessRydberg / (np.pi * alpha * self.settings['epsilond']))
        print(type(self.z_mesh))
        if not self.has_back:
            self.ddotStencil = differentiationStencil.FourthOrderSecondDerivative(self.z_mesh*1e7)
            self.ddotStencil = sparse.csr_matrix(self.ddotStencil.get_stencil())
        else:
            print("DOING IT HALF")
            midpoint = self.z_mesh[-1]/2
            midInd = bisect.bisect_left(self.z_mesh, midpoint)
            self.ddotStencil = differentiationStencil.FourthOrderSecondDerivative(self.z_mesh[:midInd-1]*1e7)
            self.ddotStencil = sparse.csr_matrix(self.ddotStencil.get_stencil())
            self.ddotStencilBack = differentiationStencil.FourthOrderSecondDerivative(self.z_mesh[midInd:]*1e7)
            self.ddotStencilBack = sparse.csr_matrix(self.ddotStencilBack.get_stencil())
            self.midInd = midInd

    #  Override for Schrodinger Equations
    def hole_density(self, v, Ef, update=False):
        """ Computes the hole-gas spatial distribution. If 'quantum' is True, uses a the quantum hole-gas model (Schrodinger-Poisson),
        if False, simply uses Fermi-Dirac integrals, and 'updateQuantum' decides whether to recompute the wavefunctions or not.
        If wavefunctions are not recomputed, the hole density is simply rescaled according to the change in potential by
        adding the change in potential to the F-D integrals."""
        h = np.zeros(len(self.z_mesh, ))
        if update:
            # recompute eigenfunctions and eigenvalues
            self.vToPerturb = v
            self.HoleWaveFunctions(self.kT * v, self.holeDensity,
                                   np.sin(np.pi * self.z_mesh / self.z_mesh[-1]), self.num_eigen_states,
                                   self.num_basis, self.useVxc)
            for subband in range(self.num_eigen_states):
                h = h + self.eigenFuncs[:, subband, 0] * self.NVh * fdint.parabolic(
                    (-Ef + self.eigenVals[subband, 0]) / self.kT) + self.eigenFuncs[:, subband,
                                                                1] * self.NVl * fdint.parabolic(
                    (-Ef + self.eigenVals[subband, 1]) / self.kT) + self.eigenFuncs[:, subband,
                                                                2] * self.NVso * fdint.parabolic(
                    (-Ef - self.delSO + self.eigenVals[subband, 2]) / self.kT)
        else:
            deltaV = v - self.vToPerturb
            for subband in range(self.num_eigen_states):
                h = h + self.NVh * np.multiply(self.eigenFuncs[:, subband, 0], fdint.parabolic(((-Ef
                    +self.eigenVals[subband, 0]) / self.kT) + deltaV)) + self.NVl * np.multiply(self.eigenFuncs[:,
                    subband, 1], fdint.parabolic(((-Ef + self.eigenVals[subband, 1]) / self.kT) + deltaV)) \
                    + self.NVso * np.multiply(self.eigenFuncs[:, subband,2], fdint.parabolic(((-Ef
                    - self.delSO + self.eigenVals[subband, 2]) / self.kT) + deltaV))
        self.holeDensity = h
        return h

    #  Override for Schrodinger Equations
    def hole_density_deriv(self, v, Ef):
        dh = np.zeros(len(self.z_mesh))
        deltaV = v - self.vToPerturb
        for subband in range(self.num_eigen_states):
            dh = dh + self.NVh * np.multiply(self.eigenFuncs[:, subband, 0], fdint.dparabolic(((-Ef
                +self.eigenVals[subband, 0]) / self.kT) + deltaV)) + self.NVl * np.multiply(self.eigenFuncs[:,
                subband, 1], fdint.dparabolic(((-Ef + self.eigenVals[subband, 1]) / self.kT) + deltaV)) \
                + self.NVso * np.multiply(self.eigenFuncs[:, subband, 2], fdint.dparabolic(((-Ef
                - self.delSO + self.eigenVals[subband, 2]) / self.kT) + deltaV))
        return dh

    #  Override for Schrodinger Equations
    def __estimate_fermi_energy__(self, v):
        try:
            # Update the wavefunctions otherwise brentq will get it wrong
            self.HoleWaveFunctions(self.kT * v, np.zeros(len(self.z_mesh)),
                                   self.num_eigen_states,
                                   self.num_basis, self.useVxc)
            Ef = brentq(self.integrated_charge, -(self.kT*np.max(v)+10), self.kT*np.max(v)+10,
                             args=v, xtol=self.settings['fermi_solve_brentq_tol'])
        except (RuntimeError, RuntimeWarning, TypeError, ValueError) as e:
            traceback.print_exc()
            Ef = 3.7
        return Ef

    def HoleWaveFunctions(self, vOfZ, holeDensity, Nstates, NBasis, useVxc):
        zMesh = np.longdouble(self.z_mesh)
        if not self.has_back:
            guess = np.sin(2*np.pi * self.z_mesh / self.z_mesh[-1])
            guess[0] = 0
            guess[-1] = 0
            guess = np.longdouble(guess/np.sqrt(trapz(np.multiply(np.conj(guess), guess), self.z_mesh)))
            vOfZ = np.longdouble(vOfZ)
            wavefunctions = np.zeros((len(zMesh), Nstates, 3))  # Order is heavy, light, split-off
        else:
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
                wavefunctions[:, :, i], energies[:, i] = self.Lanczos(zMesh, vOfZ, holeDensity, guess, Nstates, NBasis,
                                                                      masses[i], False, useVxc)
            else:
                halfway = np.int(Nstates/2)
                wavefunctions[:self.midInd-1, :halfway, i], energies[:halfway, i] = self.Lanczos(zMesh, vOfZ, holeDensity, guess, halfway, NBasis, masses[i], False, useVxc)
                wavefunctions[self.midInd:, halfway:, i], energies[halfway:, i] = self.Lanczos(zMeshBack, vOfZBack, holeDensityBack, guessBack, halfway, NBasis, masses[i], True, useVxc)
        self.eigenFuncs = wavefunctions
        self.eigenVals = -1*energies # easier to keep track of this minus sign here rather than in hole density function
        return

    def Hamiltonian(self, vOfZ, Vxc, m, func, backSurf):
        func[0] = 0
        func[-1] = 0
        if not backSurf:
            ddot = self.ddotStencil.dot(func)*1e-14
        else:
            ddot = self.ddotStencilBack.dot(func)*1e-14
        Ham = np.longdouble(-(self.h_bar * self.h_bar / (2 * m)) * ddot - np.multiply(vOfZ, func) + np.multiply(func, Vxc))
        return Ham

    def exchangeCorr(self, m, holeDensity):
        astar = 4 * np.pi * self.settings['epsilond'] * fc.epsilon0 * self.h_bar * self.h_bar / (m * fc.e * fc.e)
        Vxc = self.kT * self.XCconst * (np.power((4 / 3) * np.pi * holeDensity, 1 / 3) + (0.7734 / (21 * astar)) * np.log(
            1 + 21 * astar * np.power((4 / 3) * np.pi * holeDensity, 1 / 3)))
        return Vxc

    def Lanczos(self, zMesh, vOfZ, holeDensity, guess, Nstates, NBasis, mass, backSurf, useVxc):
        if useVxc:
            Vxc = self.exchangeCorr(mass, np.longdouble(holeDensity))
        else:
            Vxc = 0
        a = np.longdouble(np.zeros((NBasis,)))
        b = np.longdouble(np.zeros((NBasis-1,)))
        F = np.longdouble(np.zeros((NBasis+1, len(zMesh))))
        wavefunctions = np.longdouble(np.zeros((len(zMesh), Nstates)))
        F[0, :] = guess
        temp = self.Hamiltonian(vOfZ, Vxc, mass, F[0, :], backSurf)
        a[0] = trapz(np.multiply(np.conj(F[0, :]), temp), zMesh)
        F[1, :] = temp - a[0]*F[0, :]
        for i in range(1, NBasis):
            b[i-1] = np.sqrt(trapz(np.multiply(np.conj(F[i, :]), F[i, :]), zMesh))
            F[i, :] = F[i, :]/b[i-1]
            temp = self.Hamiltonian(vOfZ, Vxc, mass, F[i, :], backSurf)
            a[i] = trapz(np.multiply(np.conj(F[i, :]), temp), zMesh)
            F[i+1, :] = temp - a[i]*F[i, :] - b[i-1]*F[i-1, :]
        MarkHamil = sparse.diags((b, a, b), offsets=(-1, 0, 1)).toarray()
        MarkHamil = np.double(MarkHamil)
        energies, vectors = eigsh(MarkHamil, k=Nstates, which='SA', return_eigenvectors=True)
        vectors = np.longdouble(vectors)
        for i in range(Nstates):
            for j in range(NBasis):
                wavefunctions[:, i] = wavefunctions[:, i] + vectors[j, i]*F[j, :]
            wavefunctions[:, i] = np.multiply(np.conj(wavefunctions[:, i]), wavefunctions[:, i])
            wavefunctions[:, i] = wavefunctions[:, i]/trapz(wavefunctions[:, i], zMesh)
        return wavefunctions, energies

    def rho_from_v(self, v, update=False):
        """Calculate the z-dependent fix and free charge density for a given v(z)."""
        rho_z = self.hole_density(v, self.Ef, update) - self.electron_density(v, self.Ef) \
                + self.total_charged_defect_density(v, self.Ef)
        return rho_z
