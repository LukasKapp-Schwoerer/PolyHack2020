from viz import mappl
from helper.data_extraction import Data_extractor
import matplotlib.pyplot as plt
import pickle
import os

data_dir = 'data/'
data_extractor = Data_extractor(data_dir)

points = data_extractor.get_operation_points()

x_coords = []
y_coords = []
ids = []
incidence_list = {}
for point in points.values():
    ids.append(point.id_index)
    x_coords.append(point.gps[0])
    y_coords.append(point.gps[1])
    incidence_list[point.id_index] = []
                        
    for connection in point.connections_outbound:
        incidence_list[point.id_index].append(points[connection.to_op].id_index)
                                            
ops = {'ID': ids,
      'x': x_coords,
      'y': y_coords,
      'IL': incidence_list}  

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


map = mappl.Map(ops, "test")
map.plotgraph(ops)
map.plotedges(ops)
map.activatebuttons()
plt.show()

'''
map = map.Map(ops, "test")
map.plotnodes()
map.plotedges()
#map.saveplot("test.html")
map.showmap()
'''