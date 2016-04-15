"""Decorator style interceptor implementation"""

import inspect
import re

from functools import wraps


def intercept(aspects=None):
    """Decorate class to intercept its matching methods and apply advices on them.

    Advices are the cross-cutting concerns that need to be separated out from the business logic.
    This decorator applies such advices to the decorated class.

    :arg aspects: mapping of joint-points to dictionary of advices. joint-points are regex
    patterns to be matched against methods of class. If the pattern matches advices available for
    the joint-point are applied to the method. Following are the identified advices:
        before: Runs before around before
        around_before: Runs before the method
        after_exc: Runs when method encounters exception
        around_after: Runs after method is successful
        after_success: Runs after method is successful
        after_finally: Runs after method is run successfully or unsuccessfully.
    """
    if aspects and not isinstance(aspects, dict):
        raise TypeError("Aspects must be a dictionary of joint-points and advices")

    def get_matching_advices(name):
        """Get all advices matching method name"""
        all_advices = dict()
        for joint_points, advices in aspects.iteritems():
            if re.match(joint_points, name):
                for advice, impl in advices.items():
                    if advice in all_advices:
                        # Give priority to method advices over wild-card advices.
                        continue
                    all_advices[advice] = impl
        return all_advices

    def apply_advices(advices):
        """Decorating method"""
        def decorate(method):  # pylint: disable=C0111
            @wraps(method)
            def trivial(cls, *args, **kw):  # pylint: disable=C0111
                if 'before' in advices:
                    advices['before'](cls, *args, **kw)
                if 'around_before' in advices:
                    advices['around_before'](cls, *args, **kw)
                try:
                    ret = method(cls, *args, **kw)
                except Exception as e:  # pylint: disable=W0703
                    if 'after_exc' in advices:
                        advices['after_exc'](cls, e, *args, **kw)
                    ret = None
                else:
                    if 'around_after' in advices:
                        advices['around_after'](cls, *args, **kw)
                    if 'after_success' in advices:
                        advices['after_success'](cls, *args, **kw)
                finally:
                    if 'after_finally' in advices:
                        advices['after_finally'](cls, *args, **kw)
                return ret
            return trivial
        return decorate

    def decorate_class(cls, *args, **kw):  # pylint: disable=W0613
        """Decorating class"""
        if not aspects:
            return cls
        # TODO: handle staticmethods
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            matching_advices = get_matching_advices(name)
            if not matching_advices:
                continue
            setattr(cls, name, apply_advices(matching_advices)(method))
        return cls
    return decorate_class
