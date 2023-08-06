__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import click
from pathlib import Path
from diamond_bandalyzer.cli import functions
from diamond_bandalyzer.cli import GLOBAL_VARS

@click.group()
@click.option('-v', '--verbose', type=int, default=1, help="0 - Silent, 1 - Warn, 2 - Info", metavar='<int>')
@click.option('--solver-types', help="Prints implemented solver types", is_flag=True,
              callback=functions.print_solvers, expose_value=False, is_eager=True)
@click.option('--defect-library', help="Prints location and contents of the defect library and quits", is_flag=True,
              callback=functions.print_library, expose_value=False, is_eager=True)
@click.option('--plot-help', help="Prints help for plotting", is_flag=True,
              callback=functions.plot_help, expose_value=False, is_eager=True)

def cli(verbose):
    GLOBAL_VARS['LOGGING_LEVEL'] = verbose


@cli.command(no_args_is_help=True)
@click.argument('directory', type=click.Path())
def init(directory):
    """Initialise solving DIRECTORY.


     Copies a default settings and defect file to the target DIRECTORY,
     these need to be modified to define the diamond to solve."""

    directory = Path(directory)
    if not directory.exists():
        click.confirm(f'Could not find dir={directory.absolute()}, do you want to make it?', abort=True)
    elif not directory.is_dir():
        click.echo(f'{directory.absolute()} is not a directory.')
        raise click.Abort
    functions.init_folder(directory)


@cli.command(no_args_is_help=True)
@click.argument('directory', type=click.Path())
@click.option('--solver-type', 'solver_type', default=None, type=str, metavar='<str>', help='diamondsolve --solver-types')
@click.option('-i', '--initial', "init_file",  type=str, metavar='<.txt>', default=None, help='solve from provided solution')
@click.option('-s', '--settings-file', "settings_file",  type=str, metavar='<.txt>', default=None, help='provide alternative settings file')
@click.option('--live-plot', 'plotQ', type=float, metavar='<float>', default=None, help="Live plot solution of single Qexternal, save and exit.")
@click.option('--plot-level', 'plot_level', type=int, metavar='<int>', default=3, help="Level of plotting desired, see diamondsolve --plot-help")
@click.option('--dry-run', 'dry_run_flag', is_flag=True, help="Do everything except solving the bands.")
@click.option('--overwrite', '-o', 'overwrite_flag', default=False, is_flag=True, help="Overwrite provided initial solution files.")
@click.option('--resolve', '-r', 'resolve_flag', default=False, is_flag=True, help="Resolve provided initial solution files.")
@click.option('--no-save', 'no_save_flag', default=False, is_flag=True, help="No solved data will be saved")
def solve(directory, solver_type, init_file, plotQ, plot_level, dry_run_flag, settings_file, overwrite_flag, resolve_flag, no_save_flag):
    """Solves the diamond in DIRECTORY.


     Solves for the band structure of a diamond with settings set
      by the settings.ini and defects by the defects.ini files
      in DIRECTORY. The solutions to each solver type will
      be stored here.
      --dry-run lets you see what will be run, useful for checking settings.
      --live-plot runs a live plot of the closest Q value to your input.
      all the data is saved as though the full Q space was run so that the
      solution can be continued by passing the solution to --initial"""
    functions.solve(directory, solver_type, init_file, settings_file, plotQ, plot_level, dry_run_flag, overwrite_flag, resolve_flag, no_save_flag)


@cli.command(no_args_is_help=True)
@click.option('--build-defaults', help="Builds a default_settings.ini from coded defaults.", is_flag=True,
              callback=functions.build_defaults, expose_value=False, is_eager=True)
def dev_ops(*args):
    """Development only operations.


     Allows certain utility functions useful only to development
     to be run. See diamond solve dev-ops --help for more information."""


def main():
    cli()


if __name__ == "__main__":
    main()