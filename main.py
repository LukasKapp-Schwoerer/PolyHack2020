from viz import mappl
from helper.data_extraction import Data_extractor
import matplotlib.pyplot as plt
import pickle
import os
import argparse
from helper.coarse import *
from datetime import date

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--coarsity", type=float)
args = parser.parse_args()

data_dir = 'data/'

data_extractor = Data_extractor(data_dir)
points = data_extractor.get_operation_points_dict()

map = mappl.Map(points, data_extractor, "test")
map.plotgraph()
map.plotedges()
map.activatebuttons()
plt.show()
