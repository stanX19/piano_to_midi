import os
import itertools


def unique_name(basename, ext):
    actual_name = "%s.%s" % (basename, ext)
    c = itertools.count()
    while os.path.exists(actual_name):
        actual_name = "%s(%d).%s" % (basename, next(c), ext)
    return actual_name
