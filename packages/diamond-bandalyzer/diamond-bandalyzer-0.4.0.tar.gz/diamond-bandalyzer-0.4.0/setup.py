from setuptools import setup, find_packages
from diamond_bandalyzer.version import __version__
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='diamond-bandalyzer',
    author='Nikolai Dontschuk, Daniel McCloskey',
    author_email='dontschuk.n@unimelb.edu.au',
    description='A free, open-source python package for solving '
                'the near surface diamond electronic band structure.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=__version__,
    packages=['diamond_bandalyzer', 'diamond_bandalyzer.cli', 'diamond_bandalyzer.validation_tests'],
    package_data={'diamond_bandalyzer': ['.config/*.ini'],
                  'diamond_bandalyzer.validation_tests': ['z_shift_test/*.ini']},

    python_requires='>3.6',
    licence='AFLv3',
    install_requires=[
        'Click',
        'numpy',
        'scipy',
        'numba',
        'matplotlib',
        'fdint',
        'numpyencoder',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'diamondsolve = diamond_bandalyzer.cli.__main__:main'
        ],
    }
    #    scripts=['diamond_bandalyzer/validation_tests/z_shift_test.py'],
)
