import os

join = os.path.join
dirname = os.path.dirname
ROOT_DIR = os.path.abspath(join(dirname(dirname(__file__)), ".."))
ASSETS_DIR = join(ROOT_DIR, "assets")
DATA_DIR = join(ROOT_DIR, "data")
VIDEOS_DIR = join(DATA_DIR, "videos")
DPF_DIR = join(DATA_DIR, "dpf")
