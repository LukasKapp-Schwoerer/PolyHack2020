import map

# Create a list of x-coordinates
x_coords = [0,1,2,3,4]
y_coords = [5,4,1,2,0]
ID = [500, 12,2,3,4]
IL = {500: [2,3], 12: [3,4], 2:[500,12], 3: [500,12] , 4:[12]}
ops = { 'ID': ID,
        'x': x_coords,
        'y': y_coords,
        'IL': IL }

map = map.Map(ops, "test")
map.plotnodes()
map.plotedges()
#map.saveplot("test.html")
map.showmap()
