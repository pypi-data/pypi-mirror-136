import numpy as np
import matplotlib.pyplot as plt

from scipy.optimize import brentq
from sys import exc_info
from fdint import parabolic

import diamond_bandalyzer
diamond_bandalyzer.SOLVER_UNIT_SYSTEM = 'legacy'
diamond_bandalyzer.update_scales()
from diamond_bandalyzer import ENERGY_SCALE, LENGTH_SCALE
import diamond_bandalyzer.fundementalconstants as fc

class bulk_Ef:
    Fermi = True
    kT = fc.k * 300
    Ef_precision = 1e-4
    Eg = 5.45 * fc.Scale(ENERGY_SCALE, 'eV')()
    mh = 1.1*fc.mo  # hole mass
    me = 0.22*fc.mo  # electron mass

    def __init__(self, single_hole_mass=True):
        self.Ei = self.Eg/2 + 0.25*self.kT*np.log(self.mh/self.me)
        self.NC = 2*(2*np.pi*self.me*self.kT/fc.h**2)**(3/2)

        if single_hole_mass:
            self.NV = 2*(2*np.pi*self.mh*self.kT/fc.h**2)**(3/2)
        else:
            raise NotImplementedError("Can ne do multi hole mass yet.")

        self.ni = np.sqrt(self.NV * self.NC) * np.exp(-self.Eg / (2 * self.kT))

    def LHS(self, Ef, defects):
        if self.Fermi:
            lhs = self.NV * (parabolic(-Ef / self.kT))
        else:
            lhs = self.ni * np.exp((self.Ei - Ef) / self.kT)
        for name, defectdict in defects.items():
            #           print(name)
            #            print(defectdict)
            if 'donor_energy' in defectdict:
                lhs = lhs + defectdict['defect_density'] * fc.Scale(LENGTH_SCALE, 'cm')()**-3\
                      / (1 + np.exp((Ef - defectdict['donor_energy']) / self.kT))
            if 'double_donor_energy' in defectdict:
                lhs = lhs + defectdict['defect_density'] * fc.Scale(LENGTH_SCALE, 'cm')()**-3\
                      / (1 + np.exp((Ef - defectdict['double_donor_energy']) / self.kT))
        return lhs

    def RHS(self,  Ef, defects):
        if self.Fermi:
            rhs = self.NC * parabolic((Ef - self.Eg) / self.kT)
        else:
            rhs = self.ni * np.exp((Ef - self.Ei) / self.kT)
        for name, defectdict in defects.items():
            if 'acceptor_energy' in defectdict:
                rhs = rhs + defectdict['defect_density'] * fc.Scale(LENGTH_SCALE, 'cm')()**-3\
                      / (1 + np.exp((defectdict['acceptor_energy'] - Ef) / self.kT))
        return rhs

    def calculate_Fermi(self, defects, plotting=False):
        steps = 1000
        Ef_space, step = np.linspace(0.0, self.Eg, steps, retstep=True)

        def total_charge(Ef):
            return (self.LHS(Ef, defects) - self.RHS(Ef, defects))

        a = -5 * fc.Scale(ENERGY_SCALE, 'eV')()
        b = 10 * fc.Scale(ENERGY_SCALE, 'eV')()
        try:
            Ef = brentq(total_charge, a, b, xtol=self.Ef_precision)
        except:
            print(f"Couldn't minimize, (a,b): ({a:.2e},{b:.2e}), (f(a),f(b)): ({total_charge(a):.2e},{total_charge(b):.2e})", exc_info()[0], exc_info()[1], exc_info()[2])
            Ef = np.NaN

        if plotting:
            plt.figure("Fermi Calculation")
            plt.semilogy(Ef_space, self.LHS(Ef_space, defects) * fc.Scale('cm', LENGTH_SCALE)()**-3, ls='', marker='+', ms=1, c='r', label="+'ve Charges")
            plt.semilogy(Ef_space, self.RHS(Ef_space, defects) * fc.Scale('cm', LENGTH_SCALE)()**-3, ls='', marker='+', ms=1, c='b', label="-'ve Charges")
            plt.plot([Ef, Ef], plt.gca().get_ylim(), ls='--', c='k')
            plt.xlabel("E (eV)")
            plt.ylabel("Charges cm$^{-3}$")
            plt.legend()
        return Ef

defect_dict = {}
defect_dict['N'] = {'defect_density': 1e17, 'donor_energy': 3.75}
defect_dict['B'] = {'defect_density': 1e18, 'acceptor_energy': 0.37}
defect_dict['SiV'] = {'defect_density': 1e13, 'acceptor_energy': 1.4, 'donor_energy': 0.3}
defect_dict['NV'] = {'defect_density': 1e13, 'acceptor_energy': 2.85, 'donor_energy': 0.75}
defect_dict['V'] = {'defect_density': 1e17, 'acceptor_energy': 2, 'donor_energy': 1.15, 'double_donor_energy': 0.55}

ef_calculator = bulk_Ef()
B_den_range = np.logspace(16, 20, num=5)
N_den_range = np.logspace(11, 20, num=1000)
SiV_den = 1e15
defect_dict['SiV']['defect_density'] = SiV_den
NV_conversion = 0.1
V_N_ratio = 0

for B_den in B_den_range:
    defect_dict['B']['defect_density'] = B_den
    ef_range = []
    for N_den in N_den_range:
        defect_dict['N']['defect_density'] = N_den*(1-NV_conversion)
        defect_dict['NV']['defect_density'] = N_den*NV_conversion
        defect_dict['V']['defect_density'] = N_den*V_N_ratio
        ef_range.append(ef_calculator.calculate_Fermi(defect_dict))

    plt.figure("Defect controlled Ef for 1e15cm3 SiV")
    plt.semilogx(N_den_range*(1+V_N_ratio)/B_den, ef_range, label=B_den)

plt.legend(title='B density (cm$^3$)')
plt.ylabel("Bulk E$_f$ (eV)")

plt.xlabel("N density as percentage of B density")
plt.xlim(0.003, 1)
plt.ylim(0.2, 0.5)
plt.title(f'SiV density {SiV_den:0.0e}cm$^3$ N->NV conversion {NV_conversion*100:0.1f}%')
plt.plot([0.065, 0.065], plt.gca().get_ylim(), c='k', ls='--', alpha=0.5, zorder=1)

# plt.xlabel("N density + V density as percentage of B density")
# plt.xlim(0.003, 1)
# plt.ylim(0.2, 0.7)
# plt.title(f'SiV density {SiV_den:0.0e}cm$^3$ V/N ratio {V_N_ratio:0.1f}')
# plt.plot([0.04, 0.04], plt.gca().get_ylim(), c='k', ls='--', alpha=0.5, zorder=1)


plt.plot(plt.gca().get_xlim(), [0.3, 0.3], c='k', ls='--', alpha=0.5, zorder=1)

plt.xticks(ticks=[0.01, 0.1, 1], labels=['1%', '10%', '100%'])
plt.show()