"""Lint ansible playbook"""

# pylint: disable=W0603,W0613

import inspect
from os.path import dirname, join
import sys
from collections import OrderedDict

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from interceptor import intercept


ANSIBLE_CLASSES = OrderedDict()  # Add class in the order they are used.


def trace_calls(frame, event, arg):
    """Trace function calls to collect ansible classes.

    Trace functions and check if they have self as an arg. If so, get their class if the class
    belongs to ansible.
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


def collect_ansible_classes():
    """Run playbook and collect classes of ansible that are run."""
    print "Gathering classes"
    sys.settrace(trace_calls)
    main()


INDENTATION, TAB, TARGET_FILE = 0, 4, join(dirname(__file__), 'call_graph_tree.txt')


def log_method_name(*arg, **kw):
    """Advice to log method name"""
    global INDENTATION
    with open(TARGET_FILE, 'a') as fptr:
        fptr.write(" " * INDENTATION + arg[1].__name__ + '\n')
        INDENTATION += TAB


def dedent(*arg, **kw):
    """Decrease indentation"""
    global INDENTATION
    INDENTATION -= TAB


def main():
    """Run playbook"""
    for flag in ('--check', '--syntax-check'):
        if flag not in sys.argv:
            sys.argv.append(flag)
    obj = PlaybookCLI(sys.argv)
    obj.parse()
    obj.run()


if __name__ == '__main__':
    collect_ansible_classes()

    # Start from scratch
    with open(TARGET_FILE, 'w') as fptr:
        fptr.write('\n')

    print "Intercepting classes"
    ASPECTS = {r'.*': dict(before=log_method_name, after_finally=dedent)}
    print "Intercepted classes", ANSIBLE_CLASSES.keys()
    for _class in ANSIBLE_CLASSES:
        intercept(ASPECTS)(_class)

    print "Running after intercepting"
    main()
