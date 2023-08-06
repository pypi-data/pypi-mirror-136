"""Utility functions and classes used in solving diamond band structure"""

__author__ = "Nikolai Dontschuk and Dan McCloskey"
__copyright__ = "Copyright 2020, Nikolai Dontschuk and Dan McCloskey"
__license__ = "Licensed under the Academic Free License version 3.0"

import json
import time
import numpy as np
import sys
import tqdm
import re
from pathlib import Path
from numba import njit
from scipy.integrate import trapz
from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d


from configparser import ConfigParser, DuplicateSectionError, DuplicateOptionError, SectionProxy, \
    MissingSectionHeaderError


def ravel_matrix_diag_set(a, val, n=None, k=0):
    """Set the diagonal and off diagonal terms of a matrix a using np.ravel.  Slightly faster to directly implement this,
    and not call this function.  Mostly here to provide the index template for off-diagonals."""
    if n is None:
        n = min(np.shape(a))
    a.ravel()[max(k, -n * k): max(0, (n - k)) * n: n + 1] = val


# ~10% faster than (np.min, np.max), extrema_fast function is stack exchange code, not subject to our copyright or licence
@njit(fastmath=True)
def extrema_fast(arr):
    n = arr.size
    odd = n % 2
    if not odd:
        n -= 1
    max_val = min_val = arr[0]
    i = 1
    while i < n:
        x = arr[i]
        y = arr[i + 1]
        if x > y:
            x, y = y, x
        min_val = min(x, min_val)
        max_val = max(y, max_val)
        i += 2
    if not odd:
        x = arr[n]
        min_val = min(x, min_val)
        max_val = max(x, max_val)
    return max_val, min_val


def int_float(x):
    f = float(x)
    i = int(f)
    if i == f:
        return i
    return f


def ini_string_to_python(v):
    """This function needs to be updated to deal with strange things in your ini file.
    Currently handles ints, floats, bool, Nonetype and lists only containing floats and ints."""
    if not v:
        return v
    try:
        v = int_float(v)
    except ValueError:
        v = str(v)
        # TODO improve robustness, currently will not handel spaces at beginning and end of string " [ [1,2,] ... ] ] "
        try:
            if v[0] == '[' and v[-1] == ']':
                if v[1] == '[' and v[-2] == ']':
                    removed_brakets = re.split('\]\s*,\s*\[', v[2:-2])
                    v = []
                    for inner_list in removed_brakets:
                        v.append([int_float(x) for x in inner_list.split(',')])
                else:
                    v = [int_float(x) for x in v[1:-1].split(',')]
            if v == 'None' or v == 'none':
                v = None
            if v == 'False' or v == 'false':
                v = False
            if v == 'True' or v == 'true':
                v = True
        except IndexError:
            raise IndexError(f"String '{v}' couldn't be parsed, as v[0], v[1] or v[-2] doesn't exist")
    return v


def solve_meshing_problem(initSoln, uniformZ):
    # Solves the mathematical problem of optimizing the mesh spacings subject to a constraint
    # plt.plot(uniformZ,defectslog)
    # plt.show()
    # initSoln = pchip(initSoln, uniformZ, extrapolate=True)
    maxPoints = len(uniformZ)
    maxDepth = uniformZ[-1]
    dx = uniformZ[1] - uniformZ[0]
    alpha = 1 / (maxDepth ** 2)
    arcLengthFunc = np.power(alpha + np.power(np.gradient(initSoln, uniformZ, edge_order=1), 2), 1 / 2)
    arcLengthFunc = gaussian_filter1d(arcLengthFunc, maxPoints * 0.01, truncate=25)
    # arcLengthFunc = arcLengthFunc/np.min(arcLengthFunc)
    # arcLengthFunc = np.log(arcLengthFunc) + 1
    monitorFunc = interp1d(uniformZ, arcLengthFunc)
    # plt.plot(uniformZ[:-1], monitorFunc(uniformZ[:-1]))
    # plt.show()
    L = np.sum(arcLengthFunc * dx)
    print(L)

    def shoot_to_the_end(numPts):
        eqErr = L / (numPts)
        z = np.zeros(numPts)
        # Start with the first mesh spacing
        dz = eqErr / monitorFunc(0)
        # Now fill in the mesh
        for i in range(numPts - 1):
            #  print(dz)
            z[i + 1] = z[i] + dz
            # Use the secant method to find the next dz such that the next interval has relative error equal to the
            # first interval (error equidistribution)
            # dz = newton(relErrRootfind, dz, args=(z[i+1], errVal), tol=1e-6)
            # print(i)
            dz = eqErr / monitorFunc(z[i + 1])
            if z[i + 1] + dz >= maxDepth:  # Made it to the end with fewer or exact number of points than needed
                try:
                    z[i + 2] = z[i + 1] + dz
                    z = z * maxDepth / z[i + 2]
                    return z
                except:
                    Warning('Unable to construct mesh with the provided maximum number of points.')
                    return None
            if i == numPts - 2:
                Warning('Unable to construct mesh with the provided maximum number of points.')
                return None
        return z

    z_mesh = shoot_to_the_end(maxPoints)
    #  print(z_mesh)
    z_mesh = np.trim_zeros(z_mesh,
                           trim='b')  # Remove excess zero values from the back (happens if fewer than maxPoints)
    print(len(z_mesh))
    return z_mesh


class ColourLoop:
    default_colours = ['orange', 'red', 'blue', 'magenta', 'black', 'cyan']

    def __init__(self, custom_colours=None):
        self.colours = custom_colours
        self.position = 0
        if self.colours is None:
            self.colours = self.default_colours

        for colour in self.colours:
            self.check_colour_exsists(colour)

    def __call__(self):
        try:
            colour = self.colours[self.position]
        except IndexError:
            self.position = 0
            colour = self.colours[self.position]
        self.position += 1
        return colour

    def top(self):
        self.position = 0

    def add_colour(self, colour):
        self.check_colour_exsists(colour)
        self.colours.append(colour)

    # TODO: make it so this raises an error if colour given isn't a colour.  For now be careful
    def check_colour_exsists(self, colour):
        pass


def sum_array_distance(array, locations):
    """Provides the absolute summed distance between the provided locations and elements in the array closest to that
    location.
    i.e. sum_locations |array[closest] - location| """
    sum = 0
    for loc, chunk in zip(locations, array_as_chunks(array, locations)):
        sum += np.sum(np.abs(chunk - array[loc]))
    return sum


def array_as_chunks(array, locations):
    """Generator that yields chunks of an array around the provided locations"""
    try:
        diffs = np.concatenate(([locations[0]], np.diff(locations) // 2, [len(array) - locations[-1]]))
    except ValueError:
        diffs = np.array((locations[0], len(array) - locations[-1]))
    for n, loc in enumerate(locations):
        yield array[loc - diffs[n]:loc + diffs[n + 1]]


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


def update_legend(ax, new_handles, new_labels):
    """Adds new handels and new labels to a matplotlib legend, checks for shared x-axis to, enforcing single legend"""
    legend_ax = ax
    old_handles = []
    old_labels = []
    max_len = 0

    # Check for any legends that share axis get their data and enforce a single legend for the shared axes.
    for joined_ax in ax.get_shared_x_axes().get_siblings(ax):
        leg = joined_ax.get_legend()
        if leg is not None:
            old_handles = leg.legendHandles
            old_labels = [text.get_text() for text in leg.texts]
            # plot the legend on the axes with the most data.
            if len(leg.legendHandles) > max_len:
                legend_ax = joined_ax
            else:
                leg.remove()
    legend_ax.legend(old_handles + new_handles, old_labels + new_labels)


def calc_line(x1, x2, y1, y2):
    m = (y2 - y1) / (x2 - x1)
    c = y1 - m * x1
    return m, c


def compress_band_data(s_mesh, max_err=1e-6, **kwargs):
    current_idx = 0
    compressed_idx = [0]
    x = s_mesh[0]
    y_set = s_mesh[1:]
    with tqdm.tqdm(total=len(x), desc="Compressing Data") as t:
        while current_idx < len(x):
            search = True
            n = 2
            while search:
                next_idx = current_idx + n
                n += 1
                for y in y_set:
                    try:
                        m, c = calc_line(x[current_idx], x[next_idx], y[current_idx], y[next_idx])
                        new_err = np.max(
                            np.abs(extrema_fast(y[current_idx + 1:next_idx] - m * x[current_idx + 1:next_idx] - c)))
                    except IndexError:
                        n = len(x) - current_idx
                        compressed_idx.append(len(x) - 1)
                        current_idx = len(x)
                        search = False
                        break
                    else:
                        if n > 500:
                            search = False
                            compressed_idx.append(next_idx)
                            current_idx = next_idx
                            break
                        if new_err > max_err:
                            search = False
                            compressed_idx.append(next_idx - 1)
                            current_idx = next_idx - 1
                            n = n - 1
                            break
            t.update(n)
    compressed_idx = np.array(compressed_idx)

    return np.vstack((x[compressed_idx], y_set.T[compressed_idx].T[0:]))


# Config parser modification so that preserves ini file comments.
class ConfigParserCommented(ConfigParser):

    def __init__(self, **kwargs):
        self.comments = None
        super().__init__(**kwargs)

    def _read(self, fp, fpname):
        """Parse a sectioned configuration file.

        Each section in a configuration file contains a header, indicated by
        a name in square brackets (`[]'), plus key/value options, indicated by
        `name' and `value' delimited with a specific substring (`=' or `:' by
        default).

        Values can span multiple lines, as long as they are indented deeper
        than the first line of the value. Depending on the parser's mode, blank
        lines may be treated as parts of multiline values or ignored.

        Configuration files may include comments, prefixed by specific
        characters (`#' and `;' by default). Comments may appear on their own
        in an otherwise empty line or may be entered in lines holding values or
        section names.
        """
        elements_added = set()
        cursect = None  # None, or a dictionary
        sectname = None
        optname = None
        lineno = 0
        indent_level = 0
        comments = {'header': {'line': [], 'inline': {}}}
        e = None  # None, or an exception
        for lineno, line in enumerate(fp, start=1):
            comment_start = sys.maxsize
            # strip inline comments
            inline_prefixes = {p: -1 for p in self._inline_comment_prefixes}
            while comment_start == sys.maxsize and inline_prefixes:
                next_prefixes = {}
                for prefix, index in inline_prefixes.items():
                    index = line.find(prefix, index + 1)
                    if index == -1:
                        continue
                    next_prefixes[prefix] = index
                    if index == 0 or (index > 0 and line[index - 1].isspace()):
                        comment_start = min(comment_start, index)
                inline_prefixes = next_prefixes
            # strip full line comments
            for prefix in self._comment_prefixes:
                if line.strip().startswith(prefix):
                    if sectname is not None:
                        if sectname not in comments:
                            comments[sectname] = {'line': [line.strip()], 'inline': {}}
                        else:
                            comments[sectname]['line'].append(line.strip())
                    else:
                        comments['header']['line'].append(line.strip())
                    comment_start = 0
                    break
            if comment_start == sys.maxsize:
                comment_start = None

            value = line[:comment_start].strip()
            if not value:
                if self._empty_lines_in_values:
                    # add empty line to the value, but only if there was no
                    # comment on the line
                    if (comment_start is None and
                            cursect is not None and
                            optname and
                            cursect[optname] is not None):
                        cursect[optname].append('')  # newlines added at join
                else:
                    # empty line marks end of value
                    indent_level = sys.maxsize
                continue
            # continuation line?
            first_nonspace = self.NONSPACECRE.search(line)
            cur_indent_level = first_nonspace.start() if first_nonspace else 0
            if (cursect is not None and optname and
                    cur_indent_level > indent_level):
                cursect[optname].append(value)
            # a section header or option header?
            else:
                indent_level = cur_indent_level
                # is it a section header?
                mo = self.SECTCRE.match(value)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        if self._strict and sectname in elements_added:
                            raise DuplicateSectionError(sectname, fpname,
                                                        lineno)
                        cursect = self._sections[sectname]
                        elements_added.add(sectname)
                    elif sectname == self.default_section:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        self._sections[sectname] = cursect
                        self._proxies[sectname] = SectionProxy(self, sectname)
                        elements_added.add(sectname)
                    # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self._optcre.match(value)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if not optname:
                            e = self._handle_error(e, fpname, lineno, line)
                        optname = self.optionxform(optname.rstrip())
                        if (self._strict and
                                (sectname, optname) in elements_added):
                            raise DuplicateOptionError(sectname, optname,
                                                       fpname, lineno)
                        elements_added.add((sectname, optname))
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            optval = optval.strip()
                            cursect[optname] = [optval]
                        else:
                            # valueless option handling
                            cursect[optname] = None
                    else:
                        # a non-fatal parsing error occurred. set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        e = self._handle_error(e, fpname, lineno, line)

            # Store Inline Comments
            if comment_start is not None:
                if sectname is not None and optname is not None:
                    if sectname not in comments:
                        comments[sectname] = {'inline': {optname: line[comment_start:].strip()}, 'line': []}
                    else:
                        comments[sectname]['inline'][optname] = line[comment_start:].strip()
        self._join_multiline_values()
        self._update_comments(comments)
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

    def _update_comments(self, comments):
        for section, com_dict in comments.items():
            com_dict['line'] = '\n'.join(com_dict['line']) + '\n'
        if self.comments is None:
            self.comments = comments
        else:
            for section, com_dict in comments.items():
                if section in self.comments:
                    for option, il_comment in com_dict['inline'].items():
                        self.comments[section]['inline'][option] = il_comment
                    if com_dict['line']:
                        self.comments[section]['line'] = com_dict['line']
                else:
                    self.comments[section] = com_dict

    def write(self, fp, space_around_delimiters=True):
        fp.write(self.comments['header']['line'] + '\n')
        super().write(fp, space_around_delimiters)

    def _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        fp.write("[{}]\n".format(section_name))
        if section_name in self.comments:
            fp.write(self.comments[section_name]['line'])
        for key, value in section_items:
            value = self._interpolation.before_write(self, section_name, key,
                                                     value)
            if value is not None or not self._allow_no_value:
                value = delimiter + str(value).replace('\n', '\n\t')
            else:
                value = ""
            comment = ''
            if section_name in self.comments and key in self.comments[section_name]['inline']:
                comment = self.comments[section_name]['inline'][key]
            fp.write("{}{} {}\n".format(key, value, comment))
        fp.write("\n")


def load_from_jsoncache(cache_dir):
    cache_dir = Path(cache_dir)
    if cache_dir.exists():
        with open(cache_dir, mode='r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError

def find_solution_settings(solution_file_path):
    sfp = Path(solution_file_path)
    datestr = str(sfp.stem).split('_')[0]
    json_file_path = sfp.parent / '.history'
    globbed = list(json_file_path.glob(datestr + '*.jsonlock'))

    # Best method:
    for jsonlock_path in globbed:
        jsonlock_dict = load_from_jsoncache(jsonlock_path)
        try:
            if Path(jsonlock_dict['solution_filename']) == sfp:
                return jsonlock_dict
            if Path(jsonlock_dict['solution_filename']).stem == sfp.stem:
                print(f" File name {Path(jsonlock_dict['solution_filename']).stem} found in jsonlock at location:\n "
                      f"{jsonlock_path.absolute}\n.  However jsonlock file path:\n"
                      f"{Path(jsonlock_dict['solution_filename']).parent}\n didn't match solution directory:\n"
                      f"{sfp.parent}\n  Using the found jsonlock, but be careful as the wrong settings may be loaded.")
                return jsonlock_dict
        except KeyError as e:
            pass


    # This might fuck up with older files and so we need to try harder.  DEPRECATED  st_ctime is not linux file creation time.
    # modified_time_str = time.strftime('_%H%M.%S', time.localtime(sfp.stat().st_ctime))
    # lookup_error = None
    # n = 1
    # last_globbed = []
    # while len(globbed) > 1:
    #     last_globbed = globbed
    #     globbed = list(json_file_path.glob(datestr + modified_time_str[:n] + '*.jsonlock'))
    #     n += 1
    # if len(globbed) == 1:
    #     return load_from_jsoncache(globbed[0])
    # print(f"JSON not found\n lookup failed with Key error:{lookup_error} not found.\n Time search method failed globing:"
    #       f"{datestr + modified_time_str[:n] } in set\n {last_globbed}.")
    return None

def normalise_inplace(vector, x=None):
     vector *= 1/trapz(np.add(np.real(vector) ** 2, np.imag(vector) ** 2), x=x)

def inner_product(a, b=None, x=None):
    if b is None:
        return trapz(np.add(np.real(a) ** 2, np.imag(a) ** 2), x=x)
    return trapz(np.multiply(np.conj(a), b).real, x=x)

def determine_length_unit(solution_settings, solver_units=False):
    if solution_settings is None:
        solution_settings = {}
    if 'length_units' in solution_settings:
        spec_units = solution_settings['length_units']
    else:
        print("Warning: assuming length units for provided initial file is cm.")
        spec_units = 'cm'
    if not solver_units:
        return spec_units
    if 'solver_units' in solution_settings:
        solv_units = solution_settings['solver_units']
    else:
        print("Warning: assuming solver units for provided initial file is nm.")
        solv_units = 'nm'
    return spec_units, solv_units

def determine_energy_unit(solution_settings):
    if solution_settings is None:
        solution_settings = {}
    if 'energy_units' in solution_settings:
        spec_units = solution_settings['energy_units']
    else:
        print("Warning: assuming energy units for provided initial file is Eh.")
        spec_units = 'Eh'
    return spec_units
