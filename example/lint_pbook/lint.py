"""A minimal example to lint playbook for undefined variables"""

# pylint: disable=W0603,W0613

# TODO: Add tests.

import inspect
import multiprocessing
import os
import sys

from ansible.cli.playbook import PlaybookCLI  # pylint: disable=E0611,F0401
from ansible.errors import AnsibleUndefinedVariable
from ansible.plugins.strategy import StrategyBase  # pylint: disable=E0611,F0401
from ansible.executor.process.worker import WorkerProcess  # pylint: disable=E0611,F0401
from collections import defaultdict
from Queue import Empty

from interceptor import intercept
from example.lint_pbook.composite_queue import CompositeQueue
# Override multiprocess Queue with Composite Queue.
multiprocessing.Queue = CompositeQueue
# Classes to intercept
ANSIBLE_CLASSES = (AnsibleUndefinedVariable, StrategyBase, WorkerProcess)
# Dictionary of task, set of its exceptions
RESULT = defaultdict(set)

# Interceptor internal method names to be skipped while backtracking through call stack.
INTERCEPTOR_INTERNAL_METHODS = {'run_advices', 'trivial'}
# Composite queue internal method names to be skipped for while backtracking through call stack.
COMPOSITE_QUEUE_INTERNAL_METHODS = {'meth', 'get_instance_attr'}
SKIP_METHODS = INTERCEPTOR_INTERNAL_METHODS.union(COMPOSITE_QUEUE_INTERNAL_METHODS)


def main():
    """Run playbook"""
    for flag in ('--check',):
        if flag not in sys.argv:
            sys.argv.append(flag)
    obj = PlaybookCLI(sys.argv)
    obj.parse()
    obj.run()


def queue_exc(*arg, **kw):
    """Queue undefined variable exception"""
    _self = arg[0]
    if not isinstance(_self, AnsibleUndefinedVariable):
        # Run for AnsibleUndefinedVariable instance
        return
    _rslt_q = None
    for stack_trace in inspect.stack():
        # Check if method to be skipped
        if stack_trace[3] in SKIP_METHODS:
            continue
        _frame = stack_trace[0]
        _locals = inspect.getargvalues(_frame).locals
        if 'self' not in _locals:
            continue
        # Check if current frame instance of worker
        if isinstance(_locals['self'], WorkerProcess):
            # Get queue to add exception
            _rslt_q = getattr(_locals['self'], '_rslt_q')
    if not _rslt_q:
        raise ValueError("No Queue found.")
    # Add interceptor exception
    _rslt_q.put(arg[3].message, interceptor=True)


def extract_worker_exc(*arg, **kw):
    """Get exception added by worker"""
    _self = arg[0]
    if not isinstance(_self, StrategyBase):
        # Run for StrategyBase instance only
        return
    # Iterate over workers to get their task and queue
    for _worker_prc, _main_q, _rslt_q in _self._workers:
        _task = _worker_prc._task
        if _task.action == 'setup':
            # Ignore setup
            continue
        # Do till queue is empty for the worker
        while True:
            try:
                _exc = _rslt_q.get(block=False, interceptor=True)
                RESULT[_task.name].add(_exc)
            except Empty:
                break


if __name__ == '__main__':
    # Disable ansible console output
    _STDOUT = sys.stdout
    fptr = open(os.devnull, 'w')  # pylint: disable=C0103
    sys.stdout = fptr

    ASPECTS = {
        r'__init__': dict(
            around_after=queue_exc
        ),
        r'run': dict(
            before=extract_worker_exc
        )
    }
    for _class in ANSIBLE_CLASSES:
        intercept(ASPECTS)(_class)
    # Run playbook in check mode.
    main()
    # Enable console output
    sys.stdout = _STDOUT

    if not RESULT:
        print "Valid playbook"
        sys.exit()
    print "Linter Output"
    print "#" * 20
    for task, errors in RESULT.items():
        print 'Task: {1}{0}{2}{0}'.format('\n', task, '\n'.join(errors))
