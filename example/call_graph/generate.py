#!/usr/bin/env python
"""Generate call graph for a playbook execution

The call graph can be formatted into a tree structure using tool created here:
https://github.com/sans-sense/Utils
"""

# pylint: disable=C0103

import argparse
import inspect
import sys

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from collections import OrderedDict
from os.path import abspath, dirname, exists, join

from example.call_graph.advices import decrease_depth, increase_depth, write
from example.call_graph.utils import suppressConsoleOut
from interceptor import intercept


ANSIBLE_CLASSES = OrderedDict()  # Add class in the order they are used.
DESCRIPTION = ("The tool generates the call graph when a playbook is run after ansible classes "
               "are intercepted")
IGNORE_METHODS = ["_process_pending_results", "_read_worker_result", "_wait_on_pending_results"]
TARGET_FILE = join(dirname(__file__), "call_graph.txt")


def collect_ansible_classes():
    """Run playbook and collect classes of ansible that are run."""
    def trace_calls(frame, event, arg):  # pylint: disable=W0613
        """Trace function calls to collect ansible classes.

        Trace functions and check if they have self as an arg. If so, get their class if the
        class belongs to ansible.
        """
        if event != 'call':
            return
        try:
            _locals = inspect.getargvalues(frame).locals
            if 'self' not in _locals:
                return
            _class = _locals['self'].__class__
            _class_repr = repr(_class)
            if 'ansible' not in _class_repr:
                return
            ANSIBLE_CLASSES[_class] = True
        except (AttributeError, TypeError):
            pass

    print "Gathering classes"
    sys.settrace(trace_calls)
    main()


@suppressConsoleOut
def main():
    """Run playbook"""
    for flag in ('--check',):
        if flag not in sys.argv:
            sys.argv.append(flag)
    obj = PlaybookCLI(sys.argv)
    obj.parse()
    obj.run()


def _parse_args():
    """Parse args and separate generator and playbook args."""
    class HelpOnErrorArgParser(argparse.ArgumentParser):
        """Print help message as well when an error is raised."""
        def error(self, message):
            sys.stderr.write("Error: %s\n" % message)
            self.print_help()
            sys.exit(2)

    def validate(_file):
        """Validate if the given target argument is a valid file or a valid directory"""
        _file = abspath(_file)
        if not exists(_file):
            if not exists(dirname(_file)):
                # Argparse uses the ArgumentTypeError to give a rejection message like:
                # error: argument input: x does not exist
                raise argparse.ArgumentTypeError("{0} does not exist".format(_file))
        return _file

    def expand_cg_args(cg_args):
        """Separate clubbed flags in command line args for the generator.py

        Allows flags to be clubbed like, -ilt example.txt.
        """
        expanded = list()
        for item in cg_args:
            if len(item) < 3:
                # If at all a flag, must be single flag
                expanded.append(item)
                continue
            if item.startswith("-"):
                if not item.startswith("--"):
                    for flag in item[1:]:
                        expanded.append('-' + flag)
                    continue
            expanded.append(item)
        return expanded

    class AssignDefaultIgnore(argparse.Action):
        """If argument is specified but nothing provided, use pre-defined.

        nargs="*" doesn't allow const and default kwarg can't be used as we might not want to
        ignore as well.
        """
        def __call__(self, parser, args, values, option_string=None):
            if values is not None and not len(values):
                values = IGNORE_METHODS
            setattr(args, self.dest, values)

    try:
        indx = sys.argv.index('--')
        cg_args, sys.argv = sys.argv[1:indx], sys.argv[:1] + sys.argv[indx + 1:]
    except ValueError:
        cg_args = []

    cg_args = expand_cg_args(cg_args)  # allow -il type of usage
    parser = HelpOnErrorArgParser(description=DESCRIPTION)
    parser.add_argument(
        "-l", "--long", action='store_true', default=False,
        help="File reference of method in call graph is absolute, i.e. starts with ansible, "
             "otherwise just the basename if not __init__.py")
    parser.add_argument(
        "-t", "--target", nargs="?", type=validate, const=TARGET_FILE, default=TARGET_FILE,
        help="Filepath to write call graph, defaults to %(default)s")
    parser.add_argument(
        "-i", "--ignore", nargs='*', action=AssignDefaultIgnore,
        help="Methods to ignore while generating call graph")
    # TODO: Aloow classes that can be intercepted
    parser.usage = \
        parser.format_usage()[len("usage: "):].rstrip() + " -- <ansible-playbook options>\n"
    cg_args = parser.parse_args(cg_args)

    if not len(sys.argv[1:]):
        parser.print_help()
        sys.exit(2)

    return cg_args


if __name__ == '__main__':
    cg_args = _parse_args()
    collect_ansible_classes()
    # Uncomment below for small run and comment above.
    # ANSIBLE_CLASSES[PlaybookCLI] = True
    # Start from scratch
    with open(cg_args.target, 'w') as fptr:
        fptr.write('')
    pat = r'.*'
    if cg_args.ignore:
        pat = r'^(?!%s)' % '|'.join(item + '$' for item in cg_args.ignore) + pat
    ASPECTS = {
        pat:
            dict(
                before=(increase_depth, write(cg_args.target, cg_args.long)),
                after_finally=(write(cg_args.target, cg_args.long, False), decrease_depth)
            ),
    }
    print "Intercepting ansible classes"
    for _class in ANSIBLE_CLASSES:
        intercept(ASPECTS)(_class)

    print "Running after intercepting"
    main()
