"""Advices for generating call graph"""

# pylint: disable=W0603

import inspect
import re
import os


COUNT = -1
DEPTH_MARKER = "|"
ENTER_MARKER = ">"
EXIT_MARKER = "<"
RJUST_LONG = 50
RJUST_SMALL = 25


def increase_depth(*arg, **kw):  # pylint: disable=W0613
    """Increase count of marker that signifies depth in the call graph tree"""
    global COUNT
    COUNT += 1


def write(_filename, _long, enter=True):
    """Write the call info to file"""
    def method(*arg, **kw):  # pylint: disable=W0613
        """Reference to the advice in order to facilitate argument support."""
        def get_short(_fname):
            """Get basename of the file. If file is __init__.py, get its directory too"""
            dir_path, short_fname = os.path.split(_fname)
            short_fname = short_fname.replace(".py", "")
            if short_fname == "__init__":
                short_fname = "%s.%s" % (os.path.basename(dir_path), short_fname)
            return short_fname

        def get_long(_fname):
            """Get full reference to the file"""
            try:
                return re.findall(r'(ansible.*)\.py', _fname)[-1].replace(os.sep, ".")
            except IndexError:
                # If ansible is extending some library, ansible won't be present in the path.
                return get_short(_fname)

        meth_code = arg[1].im_func.func_code
        fname, lineno, _name = meth_code.co_filename, meth_code.co_firstlineno, meth_code.co_name
        marker = ENTER_MARKER
        if not _long:
            _fname, _rjust = get_short(fname), RJUST_SMALL
        else:
            _fname, _rjust = get_long(fname), RJUST_LONG
        if not enter:
            try:
                meth_line_count = len(inspect.getsourcelines(meth_code)[0])
                lineno += meth_line_count - 1
            except Exception:  # pylint: disable=W0703
                # TODO: Find other way to get ending line number for the method
                # Line number same as start of method.
                pass
            marker = EXIT_MARKER
        with open(_filename, "a") as fptr:
            call_info = "%s: %s:%s %s%s\n" % (
                _fname.rjust(_rjust),            # filename
                str(lineno).rjust(4),            # line number
                (" %s" % DEPTH_MARKER) * COUNT,  # Depth
                marker,                          # Method enter, exit marker
                _name                            # Method name
            )
            fptr.write(call_info)
    return method


def decrease_depth(*arg, **kw):  # pylint: disable=W0613
    """Decrease count of marker that signifies depth in the call graph tree"""
    global COUNT
    COUNT -= 1
