"""Module that allows for wrapping of a solver class to produce live-plots during solving."""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import numpy as np
import matplotlib.pyplot as plt
import time
from diamond_bandalyzer.utilities import ColourLoop
import diamond_bandalyzer.fundementalconstants as fc
from . import LENGTH_SCALE, ENERGY_SCALE, POTENTIAL_SCALE
length_scale = fc.Scale('nm', LENGTH_SCALE)()
density_scale = fc.Scale('cm', LENGTH_SCALE)()**-3
areal_scale = fc.Scale('cm', LENGTH_SCALE)()**-2
energy_scale = fc.Scale('eV', ENERGY_SCALE)()
max_level = 4
colourloop = ColourLoop()


def mypause(interval):
    """Custom matplotlib pause for re-draw that doesn't steal window attention."""
    manager = plt._pylab_helpers.Gcf.get_active()
    if manager is not None:
        canvas = manager.canvas
        if canvas.figure.stale:
            canvas.draw_idle()
        canvas.start_event_loop(interval)
    else:
        time.sleep(interval)
    # input()


def add_point_to_line(line, x, y):
    line.set_xdata(np.append(line.get_xdata(), x))
    line.set_ydata(np.append(line.get_ydata(), y))


def level_0_data_poisson(obj, **kwargs):
    """[['V (eV)', 'E field (V/cm)', 'Electrons (cm-3)'],
    ['rho (C)', 'Defect charge density (cm-3)', 'Holes (cm-3)']]"""
    v = obj.s_mesh
    rho = obj.rho_from_v(v)
    efield = fc.e*obj.e_field_from_v(v, obj.z_mesh) * fc.Scale('V', POTENTIAL_SCALE)() / fc.Scale('cm', LENGTH_SCALE)()
    electrons = obj.electron_density(v, obj.Ef)*density_scale
    holes = obj.hole_density(v, obj.Ef)*density_scale
    defectdensity = obj.total_charged_defect_density(v, obj.Ef)*density_scale
    y_axis = [v*obj.kT*energy_scale, efield, electrons, rho, defectdensity, holes]
    z_mesh_nm = obj.z_mesh*length_scale
    x_axis = [z_mesh_nm for n in range(len(y_axis))]
    return x_axis, y_axis, []


def level_1_data_poisson(obj, n=0, **kwargs):
    omega = 0
    try:
        omega = obj.omegaNR
    except AttributeError:
        try:
            omega = obj.omega
        except AttributeError:
            pass
    return level_0_data_poisson(obj)[0], level_0_data_poisson(obj)[1], [[n, obj.Ef*energy_scale], [n, obj.diff], [n, omega]]


def level_2_data_poisson(obj, n=0, **kwargs):
    x, y, p = level_1_data_poisson(obj, n)
    p.append([n, obj.top_surface()])
    p.append([n, obj.back_surface()])
    return x, y, p

def level_3_data_poisson(obj, n=0, **kwargs):
    x, y, p = level_2_data_poisson(obj, n)
    x.append(obj.z_mesh)
    y.append(obj.s_mesh_last - obj.s_mesh)
    try:
        x.append(obj.z_mesh_phantom)
        y.append(obj.s_mesh_phantom)
    except AttributeError:
        pass
    return x, y, p

def level_4_data_poisson(obj, n=0, **kwargs):
    x, y, p = level_3_data_poisson(obj, n)
    bases = obj.lancoz_basis
    for i in range(4):
        x.append(obj.z_mesh)
        y.append(np.real(bases)[:-1])
        x.append(obj.z_mesh)
        y.append(np.imag(bases)[:-1])
    return x, y, p

def initialise_level(obj, z_axes, points_axes, data):
    for ax, xax, yax in zip(z_axes, data[0], data[1]):
        if len(np.shape(yax)) > 1:
            for n, a_yax in enumerate(yax):
                ax.plot(xax, a_yax, label=str(n))
            ax.legend(frameon=False)
        else:
            ax.plot(xax, yax, c=colourloop())
    colourloop.top()
    for ax, data in zip(points_axes, data[2]):
        ax.plot(*data)
    mypause(0.001)


def update_plot(obj, z_axes, points_axes, data):
    # print('difference = {}'.format(self.diff))
    # print('Qtot = {}'.format(self.totalCharge(self.Ef)))
    for ax, yax in zip(z_axes, data[1]):
        if len(np.shape(yax)) > 1:
            for a_yax, line in zip(yax, ax.get_lines()):
                line.set_ydata(a_yax)
        else:
            ax.get_lines()[0].set_ydata(yax)
        ax.relim()
        ax.autoscale_view()

    for ax, data in zip(points_axes, data[2]):
        add_point_to_line(ax.get_lines()[0], *data)
        ax.relim()
        ax.autoscale_view()
    mypause(0.001)

def clear_plots():
    plt.close('all')

def plotter(obj, **kwargs):
    plt.ion()
    update_exists_flag = False
    level = 0
    update_rate = 1
    figname = None
    if 'level' in kwargs:
        level = int(kwargs['level'])
    if 'update_rate' in kwargs:
        update_rate = int(kwargs['update_rate'])
    if 'name' in kwargs:
        figname = kwargs['name']

    if level > max_level:
        level = max_level

    gridspec = {}
    figures = np.array([])
    z_axes = np.array([])
    points_axes = []

    if level >= 0:
        figures = np.array([['V (eV)', 'E field (V/cm)', 'Electrons (cm-3)'],
                            ['rho (C)', 'Defect charge density (cm-3)', 'Holes (cm-3)']])
        get_data = level_0_data_poisson
        gridspec = {'hspace': 0.5, 'wspace': 0.3}
        figname = "Diamond Bands and Defects"

        fig, z_axes = plt.subplots(*np.shape(figures), num=figname, gridspec_kw=gridspec, figsize=(10, 5))
        figures = figures.flatten()
        z_axes = z_axes.flatten()
        for ax, title in zip(z_axes, figures):
            # ax.clear()  # redundant if a unique figure name is set.
            ax.set_title(title, y=1.08)
        get_data = level_0_data_poisson

    if level >= 1:
        _, (ax1, ax2, ax3) = plt.subplots(3, 1, num="Iteration Progression", gridspec_kw={'hspace': 0, 'left': 0.25, 'right': 0.95, 'top': 0.95}, figsize=(3, 5),
                                     sharex=True)
        points_axes.append(ax1)
        ax1.set_ylabel("Ef (eV)")
        points_axes.append(ax2)
        ax3.set_ylabel('Omega')
        points_axes.append(ax3)
        ax3.set_xlabel("Iteration number")
        ax2.set_ylabel("Step Difference")
        ax2.set_yscale('log')
        ax3.set_yscale('log')

        get_data = level_1_data_poisson

    if level >= 2:
        _, (ax1, ax2) = plt.subplots(2, 1, num="Surfaces", gridspec_kw={'hspace': 0, 'left': 0.35, 'right': 0.95, 'top': 0.95}, figsize=(3, 5),
                                     sharex=True)
        points_axes.append(ax1)
        ax1.set_ylabel("Top Surface Charge (e)")
        points_axes.append(ax2)
        ax2.set_ylabel("Back Surface Charge (e)")
        ax2.set_xlabel("Iteration Number")
        for ax in [ax1]:
            ax.set_yscale('log')
        get_data = level_2_data_poisson

    if level >= 3:
        ax1 = plt.figure("Step Soln diff", figsize=(3, 3)).gca()
        ax2 = plt.figure("Phantom Mesh", figsize=(3, 3)).gca()
        z_axes = np.append(z_axes, ax1)
        z_axes = np.append(z_axes, ax2)
        ax1.set_ylabel('S mesh diff (unitless potential)')
        ax1.set_xlabel('Z mesh (nm)')
        ax2.set_ylabel('Phantom s mesh(unitless potential)')
        ax2.set_xlabel('Z mesh (nm)')
        get_data = level_3_data_poisson

    if level >= 4:
        _, (ax1, ax2) = plt.subplots(2, 1, num="Lancoz Basis", gridspec_kw={'hspace': 0, 'left': 0.35, 'right': 0.95,
                                                                   'top': 0.95}, figsize=(3, 5), sharex=True)

        z_axes = np.append(z_axes, ax1)
        z_axes = np.append(z_axes, ax2)
        ax1.set_ylabel(f'Real Lancoz Basis')
        ax1.set_xlabel('Z mesh (nm)')
        ax2.set_ylabel(f'Imaginary Lancoz Basis')
        ax2.set_xlabel('Z mesh (nm)')


        get_data = level_4_data_poisson


    if hasattr(obj, '__updates__'):
        update_exists_flag = True

        class PlottingObj(obj):

            def __init__(self, **kwargs):
                super().__init__(**kwargs)

            def _initialise_solver_(self):
                initialise_level(self, z_axes, points_axes, get_data(self))
                super()._initialise_solver_()

            def __updates__(self, n):
                if np.mod(n, update_rate) == 0:
                    update_plot(self, z_axes, points_axes, get_data(self, n=n))
                super().__updates__(n)

            def clear_all(self):
                clear_plots()

        return PlottingObj
