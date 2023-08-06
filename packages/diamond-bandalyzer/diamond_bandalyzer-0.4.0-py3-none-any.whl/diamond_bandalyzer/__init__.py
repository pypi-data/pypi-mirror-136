import pkg_resources
CONFIG_PATH = pkg_resources.resource_filename('diamond_bandalyzer', '.config/')

SOLVER_UNIT_SYSTEM = 'legacy'
#SOLVER_UNIT_SYSTEM = 'hartree-atomic'

def update_scales():
    global LENGTH_SCALE, ENERGY_SCALE, POTENTIAL_SCALE, CHARGE_SCALE
    if SOLVER_UNIT_SYSTEM == 'hartree-atomic':
        LENGTH_SCALE = 'ka0'
        ENERGY_SCALE = 'Eh'
        POTENTIAL_SCALE = 'Eh/e'
        CHARGE_SCALE = 'e'
    else:  # SOLVER_UNIT_SYSTEM = 'legacy'
        LENGTH_SCALE = 'nm'
        ENERGY_SCALE = 'eV'
        POTENTIAL_SCALE = 'V'
        CHARGE_SCALE = 'e'


LENGTH_SCALE = None
ENERGY_SCALE = None
POTENTIAL_SCALE = None
CHARGE_SCALE = None
update_scales()



