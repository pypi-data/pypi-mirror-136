#!/usr/bin/env python
""" Python script to validate diamondsolve by solving an intrinsic H-terminated diamond to compare
to literature values determined by direct integration."""

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
#kT = fc.k * 300
kT = fc.k * 1
# ++ Module Flags for development ++ #
reuse_solve = False
DATA_PATH = Path(pkg_resources.resource_filename('diamond_bandalyzer.validation_tests', 'intrinsic_test/'))


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
    x = solution[0] * 1e7
    plt.figure("S_Mesh")
    if len(solution) == 2:
        Q, Ef = FOM[0], FOM[1]
        p = plt.plot(x, solution[1] * kT, label=f'Qsa: {Q:.0e}')
        plt.plot([min(x) - 20, max(x) + 20], [Ef, Ef], ls='--', c=p[0].get_color(), label=f'   Ef: {Ef:0.3f}')
    else:
        for y, Q, Ef in zip(solution[1:], FOM[0], FOM[1]):
            if y.any() > 0.01:
                p = plt.plot(x, y * kT, label=f'Qsa: {Q:.0e}')
                plt.plot([min(x) - 20, max(x) + 20], [Ef, Ef], ls='--', c=p[0].get_color(), label=f'   Ef: {Ef:0.3f}')
    plt.xlabel("Z (nm)")
    plt.ylabel("V (eV)")

    plt.xlim(min(x) - 20, max(x) + 20)
    plt.legend()
    plt.show()

from PIL import Image

def compare_2_literature(solution_files):

    #  The Origin is set to where the VBM touches Ef, for the images this is done via inspection.
    lit_image = DATA_PATH / "HtermHoleGas_Ristein_SurfSci600_3677_2006.png"
    lit_dim = (60.655 / (2*1.349), 39.878 / (2*81.8))  # (nm, eV)
    lit_origin = (58.5 / (2*1.349) - 0.5775, 15.15 / (2*81.8) - 0.15)  # (nm, eV)
    lit_extent = (lit_origin[0] + lit_dim[0], lit_origin[0] - lit_dim[0],
                  lit_origin[1] - lit_dim[1], lit_origin[1] + lit_dim[1])
    print(lit_extent)
    zoom_lit_image = DATA_PATH / "HtermHoleGasZoom_Ristein_SurfSci600_3677_2006.png"
    zoom_dim = (59.9 / (2*22.04), 40.152 / (2*22.11))  # (nm, eV)
    zoom_origin = (25.5 / (2*22.04) - 0.7775, 23.35 / (2*22.11) - 0.38)  # (nm, eV)
    zoom_extent = (zoom_origin[0] + zoom_dim[0], zoom_origin[0] - zoom_dim[0],
                   zoom_origin[1] - zoom_dim[1], zoom_origin[1] + zoom_dim[1])

    plt.figure("Litertaure Comparison", figsize=(5,5))
    plt.imshow(Image.open(lit_image), zorder=0, extent=lit_extent, origin='upper', aspect='auto')
    plt.xlim(*plt.gca().get_xlim())
    plt.ylim(*plt.gca().get_ylim())
    lit_graph = plt.gca()

    plt.figure("Litertaure Comparison Zoom", figsize=(5,5))
    plt.imshow(Image.open(zoom_lit_image), zorder=0, extent=zoom_extent, origin='upper', aspect='auto')
    plt.xlim(*plt.gca().get_xlim())
    plt.ylim(*plt.gca().get_ylim())
    zoom_graph = plt.gca()

    for solution_file in solution_files:
        FOM_file = str(solution_file.absolute()).replace("solution_space", "FOM")
        FOM = np.loadtxt(FOM_file).T
        solution = np.loadtxt(solution_file).T
        xtrashift = -12.4
        y = solution[1]*kT - FOM[1]
        zero_idx = np.argmin(np.abs(y))
        lit_graph.plot((solution[0] - solution[0][zero_idx]) * 1e7, y, label=solution_file.stem)
        zoom_graph.plot((solution[0] - solution[0][zero_idx])*1e7 - xtrashift, y-0.05, label=solution_file.stem)


    # plt.legend()
    plt.show()



def delete_files(files):
    for file in files:
        fomfile = file.parent / file.name.replace("solution_space", "FOM")
        file.unlink()
        fomfile.unlink()


def main():
    reuse_solve = True
    if not reuse_solve:
        completion = subprocess.run(
            ["diamondsolve", 'solve', DATA_PATH.absolute(), "--dry-run", "--solver-type", "NR_Poisson"], capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')
        if error:
            print(error)
            return 1

        print("Dry run successful, solving largest Qext with live plot")
        completion = subprocess.run(
            ["diamondsolve", 'solve', DATA_PATH.absolute(), "--live-plot", "5e13", "--solver-type", "NR_Poisson"], capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')

        completion = subprocess.run(
            ["diamondsolve", 'solve', DATA_PATH.absolute(), "--live-plot", "5e13", "--solver-type", "NR_Poisson",
             "-s", (DATA_PATH / "settings_simpleVB.ini").absolute()], capture_output=True)
        print(completion.stdout.decode('utf-8'))
        error = completion.stderr.decode('utf-8')
        print("Dry run successful, solving largest Qext with live plot")
    # completion = subprocess.run(
    #     ["diamondsolve", 'solve', DATA_PATH.absolute(), "--live-plot", "5e13", "--solver-type", "NR_Schrodinger"],
    #     capture_output=True)
    # print(completion.stdout.decode('utf-8'))
    # error = completion.stderr.decode('utf-8')
    # print(error)

    date_today = datetime.datetime.now().strftime(f'%Y%m%d')
    files = [a for a in DATA_PATH.glob(f"{date_today}_PoissonNRSolver_solution_space_*.txt")]
    files.sort(key=lambda x: x.stat().st_ctime)

    compare_2_literature(files)
    # print("Is the solution satisfactory, continue to solve all Q? [Y/y/yes]")
    # affirmative = ['y', 'ye', 'yes', 'yeah', 'yeh']
    # inputString = input().lower()
    # if inputString not in affirmative:
    #     print("You have selected NO, goodbye.")
    #     delete_files(files[:1])
    #     return 0

    #     completion = subprocess.run(
    #         ["diamondsolve", 'solve', DATA_PATH.absolute(), "-i", files[0].absolute(), '-o', "--solver-type", "NR_Poisson"],
    #         capture_output=True)
    #     print(completion.stdout.decode('utf-8'))
    #     error = completion.stderr.decode('utf-8')
    # date_today = datetime.datetime.now().strftime(f'%Y%m%d')
    # files = [a for a in DATA_PATH.glob(f"{date_today}_PoissonNRSolver_solution_space_*.txt")]
    # files.sort(key=lambda x: x.stat().st_ctime, reverse=True)
    # test_z_shift(files[0])
    # print("Would you like to delete the solution data files?")
    # inputString = input().lower()
    # if inputString not in affirmative:
    #     print("You have selected NO, goodbye.")
    #     return 0
    # delete_files(files)


if __name__ == "__main__":
    output = main()
    sys.exit(output)
