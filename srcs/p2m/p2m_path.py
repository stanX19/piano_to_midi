import os

join = os.path.join
dirname = os.path.dirname
root = os.path.abspath(join(dirname(dirname(__file__)), ".."))
assets = join(root, "assets")
data = join(root, "data")
