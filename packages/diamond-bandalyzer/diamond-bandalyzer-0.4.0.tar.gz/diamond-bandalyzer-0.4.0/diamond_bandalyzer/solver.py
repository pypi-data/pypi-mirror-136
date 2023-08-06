"""Base class for a numerical solver."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
from diamond_bandalyzer.utilities import extrema_fast
from diamond_bandalyzer.settingsobject import SettingsObject
import math


class Solver(SettingsObject):
    _settings_heading_ = "SolverBase"
    default_settings = {'accuracy': 1e-6, 'iter_max': 1e5}

    def __init__(self, z_mesh=None, init=None, z_mesh_file=None, progress_bar=False, pause_before_close=False, **kwargs):
        super().__init__(z_mesh, **kwargs)

        self.__add_default_settings__(Solver, **kwargs)
        self.unsolved = True
        self.failed = False  # Somethings gone wrong, end the iteration.
        self.from_inital_soln = False #  Did we start from an inital solution, do we need to run specific initalisations.
        self.progress_bar_flag = progress_bar
        self.progress_bar = None
        self.pause_before_close = pause_before_close

        if z_mesh is not None:
            self.z_mesh = z_mesh
            self.s_mesh = self._initialise_solution_(init)
            self.s_mesh_last = np.copy(self.s_mesh)
        elif z_mesh_file is not None:
            try:
                #load file
                self.z_mesh = np.loadtxt('/.config/{}'.format(z_mesh_file))
            except:
                IOError('z_mesh_file could not be found! This is a fatal error, please make sure to run the z_mesher.')
        else:
            RuntimeError('No z_mesh provided and no z_mesh_file found. This is a fatal error, please make sure to run '
                         +'the z_mesher or specify a z_mesh manually.')

        self.diff = 1
        self.end_condition = self.settings['accuracy']

        if self.progress_bar_flag:
            self.setup_progress_bar()
        else:
            def void():
                return
            self.update_progress_bar = void


    def __step__(self):
        """Steps the solver, needs to be implemented per solver."""
        pass

    def setup_progress_bar(self, postfix={}):
        import tqdm
        fmt = "{l_bar}{bar}| {n:.3f}/{total_fmt} [{elapsed}<{remaining}{postfix}]"
        postfix = {}
        self.progress_bar = tqdm.tqdm(initial=0, total=-math.log10(self.settings['accuracy']), bar_format=fmt, postfix=postfix)

    def update_progress_bar(self, x=None, postfix={}):
        """Code that updates progress bar"""
        if x is None:
            x = self.diff
        self.progress_bar.last_print_n = self.progress_bar.n
        self.progress_bar.last_print_t = self.progress_bar._time()
        self.progress_bar.n = min(max(0, -math.log10(x)), -math.log10(self.settings['accuracy']))
        self.progress_bar.set_postfix(postfix)
        self.progress_bar.refresh(lock_args=self.progress_bar.lock_args)


    def __updates__(self, n):
        """Any updates to variables before the current step (n)."""
        self.update_progress_bar()
        pass

    def __updated_end_condition__(self):
        """Overwrite to apply any updates to end condition, such as multiplying by variable under/over relaxation parameters."""
        return self.end_condition

    def __fail_solver__(self, msg=None):
        self.failed = True
        if msg:
            print(msg)

    def __is_solved__(self, n):
        """Applies desired check to see if system is solved, can be overridden."""
        self.diff = np.max(np.abs(extrema_fast(self.s_mesh_last-self.s_mesh)))
        return self.diff < self.__updated_end_condition__()

    def _initialise_solution_(self, init):
        if init is None:
            return np.zeros_like(self.z_mesh)
        elif type(init) is (int or float):
            print(f"Warning: assuming contant inital condition of {init}.")
            return np.zeros_like(self.z_mesh) + init
        # TODO interpolate from differently meshed soln.
        elif init.shape == self.z_mesh.shape:
            self.from_inital_soln = True
            return init
        else:
            raise NotImplementedError(f"Not sure what to do with provided initial solution. Shape {init.shape} is not {self.z_mesh.shape}")

    def _initialise_solver_(self):
        pass

    def solve(self):
        # self.unsolved = False  # hard block on running during testing/development delete when ready.
        self._initialise_solver_()
        n = 0
        while self.unsolved and not self.failed:
            np.copyto(self.s_mesh_last, self.s_mesh)  # Ensure s_mesh_last is protected from changes to s_mesh.
            self.__step__()
            self.unsolved = not self.__is_solved__(n)
            self.__updates__(n)
            if n > self.settings['iter_max']:
                self.__fail_solver__(msg=f"Maximum iterations of iter_max = {self.settings['iter_max']} reached.")
            n += 1
        self._on_solve(n)

    def _on_solve(self, n=0):
        """Run if solved itself."""
        if self.progress_bar_flag:
            self.progress_bar.close()
        print(f"Final Accuracy = {self.diff}, end_condition = {self.__updated_end_condition__()} with {n} steps")
        if self.pause_before_close:
            input()

    def get_solution(self):
        if not self.unsolved:
            return np.array(self.s_mesh)
