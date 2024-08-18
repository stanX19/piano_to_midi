import os
import itertools
import glob


def unique_name(basename, ext):
    actual_name = "%s.%s" % (basename, ext)
    c = itertools.count()
    next(c)
    while os.path.exists(actual_name):
        actual_name = "%s_%d.%s" % (basename, next(c), ext)
    return actual_name


def unique_basename(basename):
    actual_name = basename
    # Initialize the original name without the extension
    c = itertools.count()
    next(c)
    while any(glob.glob(f"{actual_name}*")):  # Check if any file starts with the basename
        actual_name = "%s_%d" % (basename, next(c))

    return actual_name


if __name__ == '__main__':
    print(unique_basename("./unique_name"))
