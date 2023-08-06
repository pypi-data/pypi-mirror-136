__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import os
import configparser
import shutil
import click
import io
from pathlib import Path
from diamond_bandalyzer.utilities import ConfigParserCommented
import diamond_bandalyzer
import diamond_bandalyzer.defects
import diamond_bandalyzer.poissonequations
import diamond_bandalyzer.poissonrelaxationsolver
import diamond_bandalyzer.poissonNRsolver
import diamond_bandalyzer.schrodpoissonequations
import diamond_bandalyzer.schrodpoissonNRsolver
import diamond_bandalyzer.solver
import diamond_bandalyzer.diamondsoln
import diamond_bandalyzer.settingsobject
from diamond_bandalyzer.cli import GLOBAL_VARS

config_folder = Path(diamond_bandalyzer.__path__[0]) / ".config"
if not config_folder.exists():
    print(f"Could'nt find .config folder!")


def safe_callback(func):
    def inner(ctx, param, value):
        if not value or ctx.resilient_parsing:
            return
        return func(ctx, param, value)

    return inner


def init_folder(directory):
    if not type(directory) is Path:
        directory = Path(directory)

    if not directory.exists():
        directory.mkdir()

    shutil.copy(config_folder / "default_settings.ini", directory / "settings.ini")
    shutil.copy(config_folder / "example_defects.ini", directory / "defects.ini")

    # Comment preserving parser.
    config_parser = ConfigParserCommented(**diamond_bandalyzer.settingsobject.config_parser_args)
    with open(directory / "settings.ini") as f:
        config_parser.read_file(f)

    # Update the values for settings_file and local_dir
    for option, value in zip(['settings_file', 'local_dir'], ["settings.ini", str(directory.absolute())]):
        config_parser.set(diamond_bandalyzer.settingsobject.SettingsObject._settings_heading_, option, value)

    with open(directory / "settings.ini", mode='w') as f:
        config_parser.write(f)


def solve(directory, solver_type, init_file, settings_file, plotQ,  plot_level, dry_run_flag, overwrite_flag, resolve_flag, no_save_flag):
    fom_file = None
    if settings_file is None:
        settings_file = "settings.ini"
    if init_file is not None:
        fom_file = Path(directory) / init_file.replace('_solution_space_', '_FOM_')
        if not fom_file.is_file():
            click.echo(f"Could'nt find matching FOM file {str(fom_file)}")
            fom_file = None
    kwargs = {}
    if GLOBAL_VARS['LOGGING_LEVEL'] > 0:
        kwargs['progress_bar'] = True
    solver = diamond_bandalyzer.diamondsoln.DiamondSoln(settings_file=str(settings_file), local_dir=directory,
                                                        dry_run=dry_run_flag, initial_solution_file=init_file,
                                                        initial_fom_file=fom_file, solver_type=solver_type,
                                                        overwrite=overwrite_flag, resolve=resolve_flag,
                                                        no_save=no_save_flag, **kwargs)
    solver.initialise()
    if plotQ is None:
        solver.solve()
    else:
        solver.plot_solve(plotQ, plot_level)
    if not dry_run_flag:
        solver.save_and_data_and_settings()

@safe_callback
def plot_help(ctx, param, value):
    click.echo("Plot things")
    ctx.exit()

@safe_callback
def print_library(ctx, param, value):
    click.echo(config_folder / "defect_library.ini")
    with open(config_folder / "defect_library.ini", mode='r') as f:
        click.echo_via_pager(f.read())
    ctx.exit()


@safe_callback
def build_defaults(ctx, param, value):
    settings_objects = [diamond_bandalyzer.diamondsoln.DiamondSoln,
                        diamond_bandalyzer.diamondsoln.FiguresOfMerit,
                        diamond_bandalyzer.defects.Defects,
                        diamond_bandalyzer.schrodpoissonNRsolver.SchrodingerPoissonNRSolver,
                        diamond_bandalyzer.poissonNRsolver.PoissonNRSolver,
                        diamond_bandalyzer.poissonrelaxationsolver.PoissonRelaxationSolver,
                        diamond_bandalyzer.schrodpoissonequations.SchrodingerPoissonEquations,
                        diamond_bandalyzer.poissonequations.PoissonEquations,
                        diamond_bandalyzer.solver.Solver,
                        diamond_bandalyzer.settingsobject.SettingsObject
                        ]
    default_settings_dict = {}
    for obj in settings_objects:
        default_settings_dict[obj._settings_heading_] = obj.default_settings
    diamond_bandalyzer.settingsobject.__create_default_ini__(default_settings_dict, preserve_comments=True, remove_old=True)
    click.echo("Created new default settings.ini from programmed defaults at ", nl=False)
    click.echo(click.style(str(config_folder / "default_settings.ini"), fg="red"))
    with open(config_folder / "default_settings.ini", mode='r') as f:
        click.echo_via_pager(f.read())
    ctx.exit()

@safe_callback
def do_nothing(ctx, param, value):
    click.echo('did nothing')
    ctx.exit()

@safe_callback
def print_solvers(ctx, param, value):
    x, y = click.get_terminal_size()
    max_len = 1
    for solver_type in diamond_bandalyzer.diamondsoln.solver_types.keys():
        max_len = max(len(solver_type), max_len)
    desc_len = max(1, x - max_len - 4)
    for solver_type, description in diamond_bandalyzer.diamondsoln.solver_types.items():
        click.echo(click.style(solver_type, fg='green'), nl=False)
        click.echo(" " * (max_len - len(solver_type) + 1) + "-- ", nl=False)
        for i in range(0, len(description[0]), desc_len):
            if i == 0:
                click.echo(description[0][i:i + desc_len])
            else:
                click.echo(" " * (x - desc_len) + description[0][i:i + desc_len])
    ctx.exit()
