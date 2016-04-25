"""Lint ansible playbook"""

# pylint: disable=W0603,W0613

# TODO: Add tests.

import inspect
from os.path import dirname, join
import sys
from collections import OrderedDict

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from interceptor import intercept


ANSIBLE_CLASSES = OrderedDict()  # Add class in the order they are used.
RESULT = list()


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
    _class, obj, meth = "", arg[0], arg[1]
    meth = meth.__name__
    if meth == "__init__":
        _class = obj.__class__.__name__
    with open(TARGET_FILE, 'a') as fptr:
        fptr.write(" " * INDENTATION + meth + (' %s' % _class).rstrip() + '\n')
        # TODO: Separate indent logic from here.
        INDENTATION += TAB


def dedent(*arg, **kw):
    """Decrease indentation"""
    global INDENTATION
    INDENTATION -= TAB


def print_args(*arg, **kw):
    """Print args for method of class"""
    print "Args for %s of class %s: %s" % (arg[1].__name__, arg[0].__class__.__name__, arg[3:])


def print_output(*arg, **kw):
    """Print output for method of class"""
    print "Out for %s of class %s: %s" % (arg[1].__name__, arg[0].__class__.__name__, arg[2])


def collect_undefined_vars(*arg, **kw):
    """Collect undefined vars"""
    # TODO: search for a more appropriate method.
    method, result = arg[1], arg[3].__dict__
    if method.__name__ == "v2_runner_on_failed":
        RESULT.append(
            "%s for %s\n%s" % (
                result['_result']['msg'], result['_task'],
                '\n'.join([i['msg'] for i in result['_result']['results']]))
        )


def main():
    """Run playbook"""
    for flag in ('--check',):
        if flag not in sys.argv:
            sys.argv.append(flag)
    obj = PlaybookCLI(sys.argv)
    obj.parse()
    obj.run()


if __name__ == '__main__':
    # TODO: Fix the logic to discover classes. Running the playbook now and later again is a
    # bad idea.
    collect_ansible_classes()
    # from ansible.inventory import Inventory
    # ANSIBLE_CLASSES[Inventory] = True

    # Start from scratch
    with open(TARGET_FILE, 'w') as fptr:
        fptr.write('\n')

    print "Intercepting classes", ANSIBLE_CLASSES.keys()
    ASPECTS = {
        r'.*': dict(before=log_method_name, after_finally=dedent),
        r'\bv2_runner_on_failed\b': dict(after_finally=(dedent, collect_undefined_vars)),
    }
    for _class in ANSIBLE_CLASSES:
        intercept(ASPECTS)(_class)

    print "Running after intercepting"
    main()

    print "Linter Output"
    print "#" * 20
    print '\n'.join(set(RESULT))
