import os
import itertools

def unique_name(basename, ext):
    actualname = "%s.%s" % (basename, ext)
    c = itertools.count()
    while os.path.exists(actualname):
        actualname = "%s(%d).%s" % (basename, next(c), ext)
    return actualname