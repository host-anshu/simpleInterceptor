"""Decorator style interceptor implementation"""

import inspect
import re

from functools import wraps


def intercept(aspects):
    """Decorate class to intercept its matching methods and apply advices on them.

    Advices are the cross-cutting concerns that need to be separated out from the business logic.
    This decorator applies such advices to the decorated class.

    :arg aspects: mapping of joint-points to dictionary of advices. joint-points are regex
    patterns to be matched against methods of class. If the pattern matches to name of a method,
    the advices available for the joint-point are applied to the method. Advices from all matching
    joint-points are applied to the method. In case of conflicting advices for a joint-point,
    joint-point exactly matching the name of the method is given preference.

    Following are the identified advices:
        before: Runs before around before
        around_before: Runs before the method
        after_exc: Runs when method encounters exception
        around_after: Runs after method is successful
        after_success: Runs after method is successful
        after_finally: Runs after method is run successfully or unsuccessfully.
    """
    if not isinstance(aspects, dict):
        raise TypeError("Aspects must be a dictionary of joint-points and advices")

    def get_matching_advices(name):
        """Get all advices matching method name"""
        all_advices = dict()
        for joint_point, advices in aspects.iteritems():
            if re.match(joint_point, name):
                for advice, impl in advices.items():
                    # Whole word matching regex might have \b around.
                    if advice in all_advices and joint_point.strip(r'\b') != name:
                        # Give priority to exactly matching method joint-points over wild-card
                        # joint points.
                        continue
                    all_advices[advice] = impl
        return all_advices

    def apply_advices(advices):
        """Decorating method"""
        def decorate(method):  # pylint: disable=C0111
            @wraps(method)
            def trivial(self, *arg, **kw):  # pylint: disable=C0111
                def run_advices(advice, extra_arg=None):
                    """Run all the advices for the joint-point"""
                    if advice not in advices:
                        return
                    advice_impl = advices[advice]
                    if not isinstance(advice_impl, (list, tuple, set)):
                        advice_impl = [advice_impl]
                    for impl in advice_impl:
                        impl(self, method, extra_arg, *arg, **kw)

                run_advices('before')
                run_advices('around_before')
                try:
                    if method.__self__ is None:
                        ret = method(self, *arg, **kw)
                    else:  # classmethods
                        ret = method(*arg, **kw)
                except Exception as e:  # pylint: disable=W0703
                    run_advices('after_exc', e)
                    ret = None
                else:
                    run_advices('around_after', ret)
                    run_advices('after_success', ret)
                finally:
                    run_advices('after_finally', ret)
                return ret
            return trivial
        return decorate

    def decorate_class(cls):
        """Decorating class"""
        # TODO: handle staticmethods
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            if method.__self__ is not None:
                # TODO: handle classmethods
                continue
            if name not in ('__init__',) and name.startswith('__'):
                continue
            matching_advices = get_matching_advices(name)
            if not matching_advices:
                continue
            setattr(cls, name, apply_advices(matching_advices)(method))
        return cls
    return decorate_class
