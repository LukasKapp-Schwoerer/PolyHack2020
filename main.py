from viz import mappl
from helper.data_extraction import Data_extractor
import matplotlib.pyplot as plt
import pickle
import os

data_dir = 'data/'
data_extractor = Data_extractor(data_dir)

points = data_extractor.get_operation_points_dict()

ccg = data_extractor.get_connection_congestions_list()
print(f"number of connection congestions: {len(ccg)}")

"""
# Create a list of x-coordinates
x_coords = [47.3913594962,46.4757535389,47.1476699285,47.1442816883,47.13816883]
y_coords = [ 8.05127371849, 8.15127371849 ,8.21849 , 8.349,  8.449]
ID = [500, 12,2,3,4]
IL = {500: [2,3], 12: [3,4], 2:[500,12], 3: [500,12] , 4:[12]}
ops = { 'ID': ID,
        'x': x_coords,
        'y': y_coords,
        'IL': IL }
cwd = os.getcwd()

filename = cwd[:-3]+"\\vis_data.pickle"
print(filename)
with open(filename, 'rb') as handle:
        ops = pickle.load(handle)
"""


map = mappl.Map(points, "test")
map.plotgraph()
map.plotedges()
map.activatebuttons()
plt.show()

'''
map = map.Map(ops, "test")
map.plotnodes()
map.plotedges()
#map.saveplot("test.html")
map.showmap()
'''
