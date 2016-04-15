"""Example advices"""

# pylint: disable=W0613


def before(*args, **kw):
    """Advice before business logic"""
    print "Entering"


def after_returning(*args, **kw):
    """Advice after business logic is run successfully"""
    print "Successfully exiting"


def after_throwing(*args, **kw):
    """Advice after business logic encounters exception"""
    print "Met exception"


def after_finally(*args, **kw):
    """Advice after business logic is successful or has met exception"""
    print "Exiting"


def around_before(*args, **kw):
    """Advice immediately before business logic"""
    print "Around(before)"


def around_after(*args, **kw):
    """Advice immediately after business logic ran successfully"""
    print "Around(after)"
