"""Solution class, handle's generating, saving and reloading solve diamond bands."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import datetime
import itertools

import traceback
import matplotlib.pyplot as plt
import math
from pathlib import Path
from diamond_bandalyzer.settingsobject import SettingsObject
from diamond_bandalyzer.defects import Defects
from diamond_bandalyzer import poissonrelaxationsolver, poissonNRsolver, schrodpoissonNRsolver
from diamond_bandalyzer.plotter import plotter
from diamond_bandalyzer.utilities import int_float, solve_meshing_problem, sum_array_distance, array_as_chunks, \
    find_nearest, find_solution_settings, determine_length_unit, determine_energy_unit
from .fundementalconstants import Scale
from . import LENGTH_SCALE, ENERGY_SCALE


from scipy.ndimage import gaussian_filter1d

from scipy.interpolate import pchip
import re


### Set values without settings###
q_r_tol = 1e-5  #  Relative tolerance on determining to two Q-space values are the same

# TODO manipulate the spacing for readability.
def make_data_comments(Qspace):
    return 'z_mesh / Q external' + ' '*4 + (' '*20).join(f"{Q:0.0e}" for Q in Qspace)


def parse_data_comments(comments):
    return np.fromstring(comments[len('# z_mesh / Q external   '):], sep=' ')


white_list_operators = ['+', '-', '/', '*', '**', '(', ')']

solver_types = {
    'Relax_Poisson': ["The relaxation method of solving the Poisson equation to determine a diamonds band structure.",
                      poissonrelaxationsolver.PoissonRelaxationSolver],
    'NR_Poisson': ["Newton Rhaphson minimisation The relaxation method of solving the Poisson equation to determine "
                   "a diamonds band structure.",
                   poissonNRsolver.PoissonNRSolver],
    'NR_Schrodinger': ["Newton Rhaphson minimisation The relaxation method of solving the Schrodinger-Poisson equation "
                       "to determine a diamonds band structure.",
                       schrodpoissonNRsolver.SchrodingerPoissonNRSolver],
}


class DiamondSoln(SettingsObject):
    _settings_heading_ = "DiamondBandSolve"
    default_settings = {'solver_type': None, 'z_mesh_definition': 'auto', 'q_external_definition': None,
                         'q_externalback_definition': None, 'diamond_thickness': 0.010, 'z_mesh_maxpoints': 5000,
                        'length_units': 'cm', 'energy_units': 'ev'}


    def __init__(self, dry_run=False, initial_solution_file=None, initial_fom_file=None, overwrite=False, resolve=False, no_save=True, **kwargs):
        super().__init__(**kwargs)
        self.__add_default_settings__(DiamondSoln, **kwargs)
        self.length_scale = Scale(LENGTH_SCALE, self.settings['length_units'])()
        self.energy_scale = Scale(ENERGY_SCALE, self.settings['energy_units'])()
        self.z_mesh = None
        self.defects = None
        self.kwargs = kwargs
        self.settings_file = None
        self.local_dir = None
        self.initial_solution = None
        self.Qspace = None
        self.solved_Qspace = None
        self.initEf = None
        self.dry_run = dry_run
        self.solver_class = None
        self.soln_space = None
        self.fom = None
        self.temp_solver_class = None
        self.initial_soln_non_zero_idx = np.array([])
        self.overwrite_file = None
        self.Qexternal_back = 0
        self.resolve_flag = resolve
        self.no_save_flag = no_save
        self.init_fom_data = None
        solution_settings = None
        if initial_solution_file is not None:
            solution_settings = find_solution_settings(initial_solution_file)
        len_unit = determine_length_unit(solution_settings)
        energy_unit = determine_energy_unit(solution_settings)
        if initial_solution_file is not None:
            initial_solution_file = Path(initial_solution_file)
            if initial_solution_file.is_file():
                self.initial_solution = np.loadtxt(initial_solution_file).T
                self.z_mesh = self.initial_solution[0]*Scale(LENGTH_SCALE, len_unit)()
                self.initial_solution = self.initial_solution[1:]
                self.initial_soln_non_zero_idx = np.ravel(np.argwhere(np.sum(self.initial_solution, axis=1) > 0))
                with open(initial_solution_file) as f:
                    first_line = f.readline()
                # just in case we didn't get given a fom file.  This is bad tho, because of rounding.
                self.solved_Qspace = parse_data_comments(first_line)
                self.settings['inital_solution_filename'] = str(initial_solution_file.absolute())
                if overwrite:
                    self.overwrite_file = initial_solution_file

        # TODO : IS this even used? If so, what for?
        self.initial_fom_file = None
        if initial_fom_file is not None:
            self.initial_fom_file = Path(initial_fom_file)
            if initial_fom_file.is_file():
                self.init_fom_data = np.loadtxt(initial_fom_file).T
                self.solved_Qspace = self.init_fom_data[0]
                self.initEf = self.init_fom_data[1]*Scale(ENERGY_SCALE, energy_unit)
                self.settings['inital_FOM_filename'] = str(initial_fom_file.absolute())
            else:
                self.initial_fom_file = None

    def initialise(self):
        # Get our settings file and local directories.
        self.settings_file = self.settings['settings_file']
        self.local_dir = self.settings['local_dir']

        # Load in our defects:
        self.kwargs['length_units'] = self.settings['length_units']
        self.defects = Defects(defects_ini='defects.ini', **self.kwargs)

        # find the chosen solver class
        if self.settings['solver_type'] not in solver_types:
            raise NotImplementedError(
                f"Solver type {self.settings['solver_type']} not implemented, see diamondsolve --solver-types.")
        self.solver_class = solver_types[self.settings['solver_type']][1]

        # Determine Q solution space definition, we floor as we only want integer Qexternal.
        Qdef = self.settings['q_external_definition']
        if Qdef is not None:
            shape = np.shape(Qdef)
            if shape:
                if shape == (3,):
                    self.Qspace = np.floor(np.linspace(*Qdef))
                elif shape[1] == 3 and shape[0] > 0:
                    self.Qspace = np.concatenate([np.linspace(*ls_def) for ls_def in Qdef])
            else:
                self.Qspace = Qdef
        # Fill out Qspace with any solved_Qspace values not defined, ensure unique Qspace.
        if self.solved_Qspace is not None:
            if np.shape(self.solved_Qspace) == ():
                self.solved_Qspace = np.array([self.solved_Qspace])
            self.Qspace = np.concatenate((self.Qspace, self.solved_Qspace))
        self.Qspace = np.unique(np.floor(self.Qspace))


        # If don't already have a z-mesh from init.
        # TODO raise warning here if settings.ini diverges from initial solution z-mesh.
        if self.z_mesh is None:
            if self.settings['z_mesh_definition'] == 'auto':
                print('Is auto z_mesh, this shit broke af')
                self.z_mesh = self.z_mesh_auto()
                plt.plot(range(len(self.z_mesh)), self.z_mesh)
                plt.show()
            else:
                self.z_mesh = self.z_mesh_from_def()
            self.z_mesh = self.z_mesh*self.length_scale  # convert to solver length scale

        # build the solution space:
        self.soln_space = np.zeros((len(self.Qspace), len(self.z_mesh)))

        # build the fom class ### THIS IS A LITMUS TEST FOR Z MESH SHARING ACROSS MULTIPLE INSTANCES
        self.temp_solver_class = self.solver_class(z_mesh=np.linspace(0,420e-9,69), Qext_top=0, defects=self.defects)
        defect_names = list(self.temp_solver_class.get_defect_densities(0, 0).keys())
        self.fom = FiguresOfMerit(defect_names, len(self.Qspace), **self.kwargs)
        self.fom.set_column(0, self.Qspace)
        if self.initial_fom_file is not None:
            self.fom.fill_from_initial(self.initial_fom_file, self.init_fom_data)

        # build any special solver args here
        if self.settings['q_externalback_definition'] is not None:
            self.Qexternal_back = float(self.settings['q_externalback_definition'])

    def solve(self):
        workers = [1]  # Dummy worker prior to multi-proccessing implementation
        ordered_qspace_pools = self.order_Qspace(workers=len(workers))

        if self.dry_run:
            print(f"Solving with {self.solver_class}.\nPassing {self.kwargs}.\nOur z_mesh:\n{self.z_mesh}\n "
                  f"It has a length of {len(self.z_mesh)} and we will need {len(self.z_mesh)*5*8e-6:0.0f}Mb of memory "
                  f"per diamond.\n Qexternal Pools: {ordered_qspace_pools}")
            print("FOM row definitions: ")
            self.fom.print_row_statements()
            return
        for worker, ordered_qspace in zip(workers, ordered_qspace_pools):
            for Qexternal in ordered_qspace:
                n = np.argmin(np.abs(self.Qspace - Qexternal))
                self.__solve_single__(n, Qexternal)

    def order_Qspace(self, workers=1):
        if self.solved_Qspace is None:
            return np.array_split(self.Qspace, workers)

        # Step 1, remove any values in Q_space to not be included.
        if not self.resolve_flag:
            Q_to_solve = []
            for n, Qexternal in enumerate(self.Qspace):
                if np.min(np.abs(Qexternal - self.solved_Qspace)) < Qexternal*q_r_tol:
                    to_init = np.argmin(np.abs(self.solved_Qspace - Qexternal))
                    if to_init in self.initial_soln_non_zero_idx:
                        # add the old solution into the new solution space for saving.
                        self.soln_space[n] = self.initial_solution[to_init]
                        continue # Don't solve this one.
                Q_to_solve.append(Qexternal)
            Q_to_solve = np.array(Q_to_solve)
        else:
            Q_to_solve = self.Qspace

        # Step 2, determine minimally distanced initial solutions to solve from.
        starting_locations = self.solved_Qspace[self.initial_soln_non_zero_idx]
        starting_idx = np.array([np.argmin(np.abs(start_loc - Q_to_solve)) for start_loc in starting_locations])

        for an_idx in starting_idx:
            minimum_distance = np.sum(np.abs(self.Qspace[an_idx] - self.Qspace))

        is_even = False
        start_points = workers
        extra_pools = 0
        if workers % 2 == 0:
            start_points = workers//2
            is_even = True
        if start_points > len(starting_idx):
            if workers < len(starting_idx):
                is_even = False
                start_points = workers
            extra_pools = start_points - len(starting_idx)

        if extra_pools < 1:
            extra_pools = 0
            possible_start_points = np.copy(starting_idx)
            lowest = -1
            low_choice = None
            also = []
            for comb in itertools.combinations(range(len(possible_start_points)), start_points):
                summed_distance = sum_array_distance(Q_to_solve, possible_start_points[np.array(comb)])
                if summed_distance < lowest or lowest < 0:
                    lowest = summed_distance
                    starting_idx = possible_start_points[np.array(comb)]

        # step 3 build a q_space list for each worker
        q_spaces = []
        chunks = list(array_as_chunks(Q_to_solve, starting_idx))
        for chunk in chunks:
            m = len(chunk) // 2
            if is_even:
                q_spaces.append(chunk[m::-1])
                q_spaces.append(chunk[m-1:])
            else:
                if len(chunks) == 1:
                    if len(chunk) == 1:
                        q_spaces.append(chunk)
                    else:
                        q_spaces.append(np.concatenate((chunk[starting_idx[0]::-1], chunk[starting_idx[0]:])))
                else:
                    q_spaces.append(np.concatenate((chunk[m::-1], chunk[m-1:])))

        # No unfilled worker pool, then we are done.
        if extra_pools < 1:
            return q_spaces

        # Manage the case where there are more workers than starting points by dividing up the current qspaces.
        num_pools = len(q_spaces)
        approx_pool_len = len(Q_to_solve)//len(starting_idx)
        n = 0
        stolen_values = []
        iii = 0
        stolen_value_idx = [[] for _ in range(num_pools)]
        while True:
            jjj = 0
            while jjj < num_pools:
                if n > approx_pool_len*extra_pools:
                    break
                stolen_values.append(q_spaces[jjj][iii])
                stolen_value_idx[jjj].append(iii)
                n += 1
            else:
                iii += 1
                continue  # only executed if the inner loop did NOT break
            break  # only executed if the inner loop DID break
        for remove_me, from_me in zip(stolen_value_idx, q_spaces):
            np.delete(from_me, remove_me)
        stolen_values = np.array(stolen_values)
        for start in range(extra_pools):
            q_spaces.append(stolen_values[start::extra_pools])


    def _best_inital_soln(self, Qexternal):
        current_soln_non_zero_idx = np.ravel(np.argwhere(np.sum(self.soln_space, axis=1) > 1))
        current_delta = None
        if current_soln_non_zero_idx.size > 0:
            # Check for nearby solution in current data set
            to_solved = np.argmin(np.abs(self.Qspace - Qexternal))
            current_idx = find_nearest(current_soln_non_zero_idx, to_solved)
            current_delta = math.fabs(current_idx - to_solved)

        # Check for nearby solution in initial data set
        to_init = None
        if self.solved_Qspace is not None:
            to_init = np.argmin(np.abs(self.solved_Qspace - Qexternal))
            initital_idx = find_nearest(self.initial_soln_non_zero_idx, to_init)
            initial_delta = math.fabs(initital_idx - to_init)
            if current_delta is None:
                return self.initial_solution[initital_idx]
            if initial_delta < current_delta:
                return self.initial_solution[initital_idx]
            else:
                return self.soln_space[current_idx]

        # Not initial solutions, use current solutions.
        if current_delta is not None:
            return self.soln_space[current_idx]

        # No where to get initial solutions from.
        return None


    def __solve_single__(self, n, Qexternal):
        initial_s_mesh = self._best_inital_soln(Qexternal)
        try:
            the_solver = self.solver_class(z_mesh=self.z_mesh, Qext_top=Qexternal, defects=self.defects,
                                           init=initial_s_mesh, Qext_back=self.Qexternal_back, **self.kwargs)
            the_solver.solve()
            self.soln_space[n] = the_solver.get_solution()
            default_values = {'Qexternal': Qexternal, 'Ef': the_solver.Ef / self.energy_scale}
            defect_values = the_solver.get_defect_densities(self.soln_space[n], the_solver.Ef, integrated=True)
            self.fom.evaluate_location(n, {**default_values, **defect_values})
        except:
            traceback.print_exc()
            print(f"Solver failed at Qexternal = {Qexternal:0.0e}")

    def plot_solve(self, Qclose, level):
        n = np.argmin(np.abs(self.Qspace - Qclose))
        Qexternal = self.Qspace[n]
        hold = self.solver_class
        self.solver_class = plotter(self.solver_class, level=level)
        self.kwargs['pause_before_close'] = True
        if self.dry_run:
            print(f"Plotting with level {level} and solving with {type(self.solver_class)}.\nPassing {self.kwargs}."
                  f"\nOur z_mesh:\n{self.z_mesh}\n It has a length of {len(self.z_mesh)} and we will need "
                  f"{len(self.z_mesh)*5*8e-6:0.0f}Mb of memory per diamond.\n Qexternal: {Qexternal}")
            print("FOM row definitions: ")
            self.fom.print_row_statements()
            return
        plt.ion()
        self.__solve_single__(n, Qexternal)
        plt.ioff()
        self.solver_class = hold

    def save_and_data_and_settings(self):
        # Grab all the settings and dump all settings to a json file
        # (duplicates automatically get eaten up by the {**dict, **dict})
        if self.no_save_flag:
            return

        # Save the data to well named files
        if self.overwrite_file is None:
            dateid = datetime.datetime.now().strftime(f'%Y%m%d_{self.solver_class._settings_heading_}')
            qrange = f'Q_{self.Qspace[0]:0.0E}_{self.Qspace[-1]:0.0E}_{len(self.Qspace):d}'.replace('+', '').replace('-',
                                                                                                                     '')
            datafile = Path(self.local_dir) / (dateid + "_solution_space_" + qrange + '.txt')
            fomfile = Path(self.local_dir) / (dateid + "_FOM_" + qrange + '.txt')
            n = 1
            while datafile.exists():
                datafile = Path(self.local_dir) / (dateid + "_solution_space_" + qrange + f'_{n}' + '.txt')
                fomfile = Path(self.local_dir) / (dateid + "_FOM_" + qrange + f'_{n}' + '.txt')
                n += 1
        else:
            datafile = self.overwrite_file
            fomfile = Path(self.local_dir) / self.overwrite_file.name.replace("solution_space", "FOM")

        settings_to_append = {}
        for obj in [self, self.fom, self.defects]:
            settings_dict = obj.save_jsoncache(dump_to_file=False)
            if settings_dict is not None:
                settings_to_append = {**settings_to_append, **settings_dict}
            else:
                # TODO log as warning
                print(f"{type(obj)} did not return any settings to dump to json dict!!!")
        # add in the saved file names.
        settings_to_append['solution_filename'] = str(datafile)
        settings_to_append['fom_filename'] = str(fomfile)
        settings_to_append['solver_units'] = LENGTH_SCALE
        # we dump from the temp_solve_class so the filename contains the solver type used.
        self.temp_solver_class.save_jsoncache(dump_to_file=True, dict_to_append=settings_to_append)

        np.savetxt(datafile, np.vstack((self.z_mesh/self.length_scale, self.soln_space)).T, header=make_data_comments(self.Qspace))
        self.fom.save_fom_to_file(fomfile)



    def z_mesh_auto(self):
        uniformZ = np.linspace(0, self.settings['diamond_thickness'], num=self.settings['z_mesh_maxpoints'])*0.1
        solutionforErr = np.zeros((len(uniformZ)))
        trialsolver = self.solver_class(z_mesh=uniformZ, Qext_top=np.mean(self.Qspace), defects=self.defects,
                                           init=solutionforErr, **self.kwargs)
        trialsolver.solve()
        solutionforErr = trialsolver.get_solution()
      #  plt.plot(uniformZ,solutionforErr)
      #  plt.show()
       # densitySpline = pchip(uniformZ, maxiondensity, extrapolate=False)
        z_mesh = solve_meshing_problem(solutionforErr, uniformZ)
        return z_mesh

    def z_mesh_from_def(self):
        z_mesh_definition = self.settings['z_mesh_definition']
        shape = np.shape(z_mesh_definition)
        # Single range
        if shape == (3,):
            # Mesh unlikely to be >1cm in spacing, assume its a linspace.
            if type(z_mesh_definition[2]) is int:
                return np.linspace(*z_mesh_definition, endpoint=True)
            return np.arange(*z_mesh_definition)
        # List of ranges
        if shape[1] == 3:
            z_mesh = np.array([])
            for single_range in z_mesh_definition:
                if type(single_range[2]) is int:
                    z_mesh = np.append(z_mesh, np.linspace(*single_range, endpoint=False))
                else:
                    z_mesh = np.append(z_mesh, np.arange(*single_range))
            return np.array(z_mesh)
        raise NotImplementedError(f"Unsure how build a z_mesh from {z_mesh_definition}")


# fname = datetime.datetime.now().strftime(f'%Y%m%d_%H%M.%S_{self._settings_heading_}_settings.jsonlock')

class FiguresOfMerit(SettingsObject):
    _settings_heading_ = "FiguresOfMerit"
    default_settings = {'row0': 'Qexternal', 'row1': 'Ef', 'row2': '', 'row3': ''}
    default_variable_names = ['Qexternal', 'Ef']

    def __init__(self, defect_names, length, **kwargs):
        super().__init__(**kwargs)
        self.__add_default_settings__(FiguresOfMerit, **kwargs)

        self.all_variable_names = [] + self.default_variable_names + [name + '--' for name in defect_names] + [
            name + '++' for name in defect_names] + [name + '-' for name in defect_names] \
                                  + [name + '+' for name in defect_names] + defect_names
        self.all_variable_names.sort(key=len, reverse=True)


        # parse_rows
        self.rows = []
        n = 0
        n_blank = 0
        self.header = ''
        adjust = 2
        while f"row{n}" in self.settings:
            if self.settings[f"row{n}"]:
                self.rows.append(self.parse_fom_instruction(self.settings[f"row{n}"], n))
                self.header += self.settings[f"row{n}"] + ' '*(25-len(self.settings[f"row{n}"]) - adjust)
                adjust = 0
            else:
                n_blank += 1
            n += 1

        # build fom data
        self.data = np.zeros((length, n - n_blank))

    def save_fom_to_file(self, file_name):
        # Find the file we are going to save at.
        file = Path(self.settings['local_dir']) / file_name
        if file.exists():
            # TODO log as warning
            print(f'Figures of merit file {file} already exists, overwriting.')
        np.savetxt(file, self.data, header=self.header)

    def parse_fom_instruction(self, string, n=None):
        characters = string.split(' ')
        for idx, char in enumerate(characters):
            if char in white_list_operators:
                pass
            elif char in self.all_variable_names:
                characters[idx] = f"values_dict['{char}']"
            else:
                try:
                    characters[idx] = str(int_float(char))
                except ValueError:
                    raise ValueError(
                        f"Illegal operator character {char} or unknown variable in figures of merit row {n} "
                        f"definition -> {string}")
        return "".join(characters)

    def evaluate_location(self, location, values_dict):
        for n, row in enumerate(self.rows):
            self.data[location][n] = eval(row)

    def set_column(self, column, values):
        self.data.T[column] = values

    def print_row_statements(self):
        for row in self.rows:
            print(row)

    def fill_from_initial(self, filename, initial_data=None):
        # ### Check that the row definitions have not changed ### #
        # Load in initial FOM file definitions from file header comments, clean whitespace and split.
        with open(filename) as fom:
            raw_row_definitions = fom.readline().strip('#').strip().split('  ')
        rows = []
        for row in raw_row_definitions:
            if row.strip():
                rows.append(row.strip())
        new_rows = []
        n = 0
        # Grab current row definitions from settings.
        while f"row{n}" in self.settings:
            if self.settings[f"row{n}"]:
                new_rows.append(self.settings[f"row{n}"])
            n += 1
        # Work out mapping between old rows and current rows.  Raise warning if any initial rows have no mapping.
        row_mapping = []
        alignment_row_old = None
        alignment_row_new = None
        for old_pos, row in enumerate(rows):
            try:
                new_pos = new_rows.index(row)
            except ValueError:
                # TODO: Log as WARNING
                print(f"WARNING: initial FOM file row {row} not specified by current row definitions (in settings.ini), "
                      f"this rows initial data will not be preserved in the new FOM file.")
            else:
                # Align on the Qexternal rows, order agnostic.
                if row == 'Qexternal':
                    alignment_row_old = old_pos
                    alignment_row_new = new_pos
                row_mapping.append([old_pos, new_pos])
            # We need alignment rows, and they need to make sense.  If the solver uses something other than Qexternal,
            # then they you are beyond my help.  Add to this for your usecase.
            if alignment_row_new is None or alignment_row_old is None:
                # TODO: Log as WARNING
                print(f"WARNING: Cannot find Qexternal data in initial or new FOM defition.  Cannot include initial FOM"
                      f"file data in new FOM save.  You'll need to extend this functionality yourself.")
                return
        # Check if we have initial FOM data, if not get it.
        if initial_data is None:
            initial_data = np.loadtxt(filename).T
        # ### Fill out new FOM data ### #
        for this_idx, this_q in enumerate(initial_data[alignment_row_old]):
            # Find the correct Q external location, within a relative tolerance.
            if np.min(np.abs(this_q - self.data.T[alignment_row_new])) < this_q * q_r_tol:
                idx = np.argmin(np.abs(this_q - self.data.T[alignment_row_new]))
                for old_pos, new_pos in row_mapping:
                    self.data[idx][new_pos] = initial_data[old_pos][this_idx]


