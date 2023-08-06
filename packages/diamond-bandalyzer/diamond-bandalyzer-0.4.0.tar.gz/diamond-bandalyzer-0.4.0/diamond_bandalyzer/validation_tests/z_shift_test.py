#!/usr/bin/env python
""" Python script to validate diamondsolve by solving a uniform N implant density diamond with no back surface
and ensure that the surface voltage as a function of surface charge is equal to band bending V as a function of
 integrated charge from z(V) into the bulk.  i,e,  Vs(Qsa) = V(int_z(v)^inf rho(z).dz.  This is equivalent to
 Vs(Qsa) being solved for all Qsa < Qsa_max once a diamond with Qsa_max has been solved.

 This works because with a uniform charge density can be reduced to a single integral equation, which is invariant
 under z-> z+dz transformation.  See supp info for doi:10.1038/s41928-018-0130-0"""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import subprocess
import sys
import datetime
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import diamond_bandalyzer.fundementalconstants as fc
from scipy.interpolate import interp1d
import pkg_resources


# ++ Constants ++ #
kT = fc.k*300
# ++ Module Flags for development ++ #
reuse_solve = False
DATA_PATH = Path(pkg_resources.resource_filename('diamond_bandalyzer.validation_tests', 'z_shift_test/'))


def read_comments(file, skiprows=0):
    comments = ''
    with open(file, mode='r') as f:
        this_line = f.readline()
        for n in range(skiprows):
            this_line = f.readline()
        while this_line:
            if this_line[0] == "#":
                comments += this_line
            this_line = f.readline()
    return comments


def plot_s_mesh(solution_file):
    FOM_file = str(solution_file.absolute()).replace("solution_space", "FOM")
    FOM = np.loadtxt(FOM_file).T
    solution = np.loadtxt(solution_file).T
    x = solution[0]*1e7
    plt.figure("S_Mesh")
    for y, Q, Ef in zip(solution[1:], FOM[0], FOM[1]):
        if y.any() > 0.01:
            p = plt.plot(x, y*kT, label=f'Qsa: {Q:.0e}')
            plt.plot([min(x) - 20, max(x) + 20], [Ef, Ef], ls='--', c=p[0].get_color(), label=f'   Ef: {Ef:0.3f}')
    plt.xlabel("Z (nm)")
    plt.ylabel("V (eV)")

    plt.xlim(min(x)-20, max(x)+20)
    plt.legend()
    plt.show()


def test_z_shift(solution_file):
    FOM_file = str(solution_file.absolute()).replace("solution_space", "FOM")
    FOM = np.loadtxt(FOM_file).T
    solution = np.loadtxt(solution_file).T
    z = solution[0]*1e7
    idx_maxQ = np.argmax(FOM[0])
    maxQ_y_x = interp1d(solution[idx_maxQ+1]*kT, z)  # numerical inversion :)
    maxQ_x_y = interp1d(z, solution[idx_maxQ+1]*kT)
    plt.figure('Z_shift')
    plt.plot(z, solution[idx_maxQ+1]*kT, label=f'Qsa: {float(FOM[0][idx_maxQ]):.0e}')
    differences = {}
    for this_idx, y in enumerate(solution[1:]):
        y = y*kT
        if this_idx == idx_maxQ:
            pass
        else:
            z_shift = maxQ_y_x(y[0])
            plt.plot(z + z_shift, y, label=f'Qsa: {float(FOM[0][this_idx]):.0e}')
            overlap_idx = np.where(z + z_shift < max(z))
            differences[str(FOM[0][this_idx])] = (maxQ_x_y(z[overlap_idx] + z_shift) - y[overlap_idx])
    plt.xlabel("Z (nm)")
    plt.ylabel("V (eV)")
    plt.legend(frameon=False, title="Solved with:")
    plt.figure("Z-shift Error")
    diff_max = 0
    for Q, dif in differences.items():
        if abs(max(dif)) > diff_max:
            diff_max = abs(max(dif))
        plt.plot(dif, label=f'Qsa: {float(Q):.0e}')
    plt.xlabel("S_mesh Index")
    plt.ylabel("zshift - Full Q solve (eV)")
    plt.legend()
  #  plt.show()
    if diff_max < 0.005:
        print("z-shift error is below 5meV, we currently consider this a success.")
    plt.show()

def delete_files(files):
    for file in files:
        fomfile = file.parent / file.name.replace("solution_space", "FOM")
        file.unlink()
        fomfile.unlink()

def main():
    if not reuse_solve:
        completion = subprocess.run(["diamondsolve", 'solve', DATA_PATH.absolute(), "--dry-run", "--solver-type", "NR_Poisson"], capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')
        if error:
            print(error)
            return 1

        print("Dry run successful, solving largest Qext with live plot")
        completion = subprocess.run(["diamondsolve", 'solve', DATA_PATH.absolute(), "--live-plot", "5e13", "--solver-type", "NR_Poisson"], capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')

        date_today = datetime.datetime.now().strftime(f'%Y%m%d')
        files = [a for a in DATA_PATH.glob(f"{date_today}_PoissonNRSolver_solution_space_*.txt")]
        files.sort(key=lambda x: x.stat().st_ctime)

 #       plot_s_mesh(files[0])
 #       print("Is the solution satisfactory, continue to solve all Q? [Y/y/yes]")
 #       affirmative = ['y', 'ye', 'yes', 'yeah', 'yeh']
 #       inputString = input().lower()
 #       if inputString not in affirmative:
 #           print("You have selected NO, goodbye.")
 #           delete_files(files[:1])
 #           return 0

        completion = subprocess.run(
            ["diamondsolve", 'solve', DATA_PATH.absolute(), "-i", files[0].absolute(), '-o', "--solver-type", "NR_Poisson"],
            capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')
    date_today = datetime.datetime.now().strftime(f'%Y%m%d')
    files = [a for a in DATA_PATH.glob(f"{date_today}_PoissonNRSolver_solution_space_*.txt")]
    files.sort(key=lambda x: x.stat().st_ctime, reverse=True)
    test_z_shift(files[0])
   # print("Would you like to delete the solution data files?")
   # inputString = input().lower()
   # if inputString not in affirmative:
   #     print("You have selected NO, goodbye.")
   #     return 0
   # delete_files(files)



if __name__ == "__main__":
    output = main()
    sys.exit(output)
