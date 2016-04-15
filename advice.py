__author__ = 'anshuc'


def before(*args, **kw):
    print "Entering advice"


def after_returning(*args, **kw):
    print "Successfully exiting advice"


def after_throwing(*args, **kw):
    print "Exception exiting advice"


def after_finally(*args, **kw):
    print "Compulsorily exiting advice"


def around_before(*args, **kw):
    print "Around before advice"


def around_after(*args, **kw):
    print "Around after advice"
