# Bandalyzer

Highly customisable analysis of electronic bands in diamond, with a particular focus on near surface electronics.

**Installation instructions:**\
`pip install diamond-bandalyzer`

To use the solver run:
`$diamondsolve` \
For now the built in help, .ini file comments and the incomplete source-code comments are the only sources of documentation.

**Basic usage pathway:**\
First initalise the directory where you want to keep the solutions with:
`$diamondsolve init <directory>`

In that directory a settings.ini and defects.ini file will be created.  Modify these files so that you are solving the diamond
of interest.  You can check if you are happy with the chosen parameters before running with:\
`$diamondsolve solve <directory> --dry-run`

It can also be very instructive to live-plot a single surface charge (q_external) before solving for the full range:\
`$diamondsolve solve <directory> --live-plot <a single Q_external>`

This will solve for the closest q_external specified in the the settings.ini to the chosen single q_external value. The
output is saved as a .txt file and can be re-input when solving the rest of the diamond with:\
`$diamondsolve solve -i <output solution space>`

To partially validate the solver you can run the z_shift_test.py script found in the validation_tests sub package.


**For development:**\
Install virtualenv on your system (preferably through your package manager 'python-virtualenv', or pip install virtualenv)
In the project folder (bandalyzer/) run:\
`$virtualenv venv`\
or if you want the virtualenv to symlink to use your system packages that already exsit.\
`$virtualenv venv --system-site-packages`

If you have multiple versions of python installed you may need to specify python 3.8, see https://virtualenv.pypa.io/en/stable/ for more information.

To activate your new python virtual environment from the project folder (or anywhere just adjust path accordingly)\
`$. venv/bin/activate`

This should drop you into the virtual environment shell
`(venv) [ ... ]$`

From the project folder, and whilst in the virtual environment run:\
`(venv) [ ... ]$pip install . -e`

This will install the project into the virtualenv, the -e flag tells pip it is editable, so any changes you make to the code
will be incorporated into the program (technically instead of installing the package as an unchangeable .egg, the .egg is just a symlink to the src-code)

From here on out, when things don't work/throw errors we submit it as an issue into gitlab :)

If you want tab completion for filenames to work within the diamondsolve command we need to add an activation script to your shell completer.
This script is auto generated for bash by running (see https://click.palletsprojects.com/en/7.x/bashcomplete/ for other shells):\
`$DIAMONDSOLVE_COMPLETE=source_bash diamondsolve`

In arch with bash shell using bash-completion i did this:\
`sudo _DIAMONDSOLVE_COMPLETE=source_bash diamondsolve > /usr/share/bash-completion/completions/diamondsolve`


**TODO**\
Solver code:
* [x] Not have functions do things other than named, i.e. e_field_from_rho computing e_field_from_v in SP-NR solver.
* [x] Have schordingerpoissonequation class inherit poissonequation class, to remove repeated code!
* [x] Estimator function for the inital Fermi level of a diamond, build in PossionEquations Class.
* [x] Plotting framework than can wrap solver/equation class and provide live plots of solution defect densities
* [x] Get rewritten relaxation solver to converge.
* [x] Get NR solver to converge
* [ ] Extend the defect.ini to include general acceptor/donor surface states, removing the sp2 definition from settings.ini.
* [x] NewtonRhapsonPoisson solver class, inherets solver, poissonequations. Uses NewtonRhapson over Relaxation.
* [x] Schrodinger-poissonequation class, inherets poissonequations. Solves schordinger equation near surface to ensure quantum properties of holes accounted for.
* [x] Full solve to obtain V(Qsa, z), diamond potential for a given adsorbed charge.
* [ ] Implement Logger, Logging and optional Log saving.
* [ ] Generalise the solver with a materials class and library that can be taken (inherited) by PoissonEquations and provide relevant equations.
* [ ] Auto z-mesh generator
* [ ] Derivative stencils can be reused with changing Qexternal
* [ ] Find alternate instantiation path to avoid too-high memory situation, i.e.e len(z_mesh)**2*8)B currently required for stencil definition.
* [ ] Improve method of monitoring excess charges in solutions.
* [ ] Solve to step change convergence (average step change constant over some window).

Testing:
* [ ] Testing framework that ensures potential/e-field/charge density equations give correct outputs.
* [ ] Testing framework that plots diamond defect definitions (to rapidly visualise poorly implemented diamonds). Started - see devOnly/structure_test.py
* [ ] Testing framework that plots and compares specific solutions (no defects, constant defect) to original method and published theory.
* [x] Ensure no settings names are capitalised - automate if need to be done again.

Validation:
* [x] Add z-shift validation test.

Settings:
* [x] Saving and loading of Settings in JSON files, build in SettingsObject base class.
* [x] Create comments for default-settings.ini
* [ ] Automatically store and add comments default-settings.ini
* [x] Function that strips and applies comments to a .ini file, so the the default-settings comments can propagate to instance settings files.
* [ ] Allow for capitalised settings names - maybe?

CLI:
* [x] Implment command line interface, CLI, for initalising and solving diamonds.
* [ ] Plot help automatically generate help option documentation from plotting definition comments.
* [ ] Implement check command.
* [ ] Implement progress bar.

Packaging:
* [x] Make it so that config files get copied on pip install
* [x] Learn how to manage a package on PyPi
* [ ] Fix FDint so that a c++ compiler is not required to install, pre-complied wheel?  Look into it.

Check command needs to check:
* [ ] Solver type exists
* [ ] Array sizes make sense
* [ ] Generate expected resource utilisation, memory, CPU core running time.

Documentation:
* [ ] Add surface charge calculations and mathematical convolution approach to latex.
* [ ] Add newton rhapson solver to latex.
