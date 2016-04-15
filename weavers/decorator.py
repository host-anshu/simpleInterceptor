__author__ = 'anshuc'

"""Decorator style weaver implementation"""

import inspect
import re
from advice import *

ASPECTS = dict()

ASPECTS[r'.*'] = dict(
    # advices for the joint-point(method name) matching any character
    before=before,
    after_finally=after_finally,
)
ASPECTS[r'hello_world'] = dict(
    # advices for the joint-point(method name) matching hello_world
    around_before=around_before,
    around_after=around_after,
    after_success=after_returning,
)
ASPECTS[r'division'] = dict(
    # advices for the joint-point(method name) matching division
    around_before=around_before,
    after_exc=after_throwing,
    around_after=around_after,
    after_success=after_returning,
)


def intercept(aspects=None):
    """Class-level decorator interceptor"""
    if not aspects:
        aspects = ASPECTS
    else:
        if not isinstance(aspects, dict):
            raise TypeError("Aspects must be a dictionary of joint-points and advices")

    def get_matching_advices(name):
        """Get all advices matching method name"""
        all_advices = dict()
        for joint_points, advices in aspects.iteritems():
            if re.match(joint_points, name):
                all_advices.update(advices)
        return all_advices

    def apply_advices(advices):
        """Decorator to apply advices"""
        def decorate(method):
            def trivial(cls, *args, **kw):
                if 'before' in advices:
                    advices['before'](cls, *args, **kw)
                if 'around_before' in advices:
                    advices['around_before'](cls, *args, **kw)
                try:
                    ret = method(cls, *args, **kw)
                except Exception as e:
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

    def decorate_class(cls, *args, **kw):
        # TODO: staticmethods
        for name, method in inspect.getmembers(cls, inspect.ismethod):
            matching_advices = get_matching_advices(name)
            if not matching_advices:
                continue
            setattr(cls, name, apply_advices(matching_advices)(method))
        return cls
    return decorate_class


if __name__ == '__main__':

    from primary_concern import PrintOutput

    # Only primary concern
    obj = PrintOutput()
    obj.hello_world()
    obj.division(4, 2)

    # Weaving decorator way.
    PrintOutput = intercept()(PrintOutput)

    # Added cross-cutting concerns.
    obj = PrintOutput()
    obj.hello_world()
    obj.division(4, 2)
    obj.division(4, 0)
