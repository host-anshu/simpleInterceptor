"""Lint ansible playbook"""

# pylint: disable=W0613

import inspect
import sys

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from interceptor import intercept


ANSIBLE_CLASSES = set()


def trace_calls(frame, event, arg):
    """Trace function calls to collect ansible classes.

    Trace functions and check if they have self as an arg. If so, get their class if the class
    belongs to ansible.
    """
    if event != 'call':
        return
    try:
        _frame = inspect.getframeinfo(frame)
    except AttributeError:
        return
    _func = _frame.function
    _locals = _func, inspect.getargvalues(frame).locals
    try:
        if 'self' not in _locals[1]:
            return
        _self = _locals[1]['self']
        _class = _self.__class__
        _class_repr = repr(_class)
        if 'ansible' not in _class_repr:
            return
        ANSIBLE_CLASSES.add(_class)
    except (AttributeError, TypeError):
        pass


def collect_ansible_classes():
    """Run playbook and collect classes of ansible that are run."""
    print "Gathering classes"
    sys.settrace(trace_calls)
    main()


def log_method_name(*arg, **kw):
    """Advice to log method name"""
    print "Advising", arg[1].__name__


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

    print "Intercepting classes"
    ASPECTS = {r'.*': dict(before=log_method_name)}
    for _class in ANSIBLE_CLASSES:
        intercept(ASPECTS)(_class)

    print "Running after intercepting"
    main()
