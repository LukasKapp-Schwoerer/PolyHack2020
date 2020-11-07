import map
import mappl
import matplotlib.pyplot as plt
# Create a list of x-coordinates
x_coords = [47.3913594962,46.4757535389,47.1476699285,47.1442816883,47.13816883]
y_coords = [ 8.05127371849, 8.15127371849 ,8.21849 , 8.349,  8.449]
ID = [500, 12,2,3,4]
IL = {500: [2,3], 12: [3,4], 2:[500,12], 3: [500,12] , 4:[12]}
ops = { 'ID': ID,
        'x': x_coords,
        'y': y_coords,
        'IL': IL }

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
