import numpy as np
from helper.data_extraction import Congestion

class Meta_connection_congestion:
    def __init__(self):
        self.congestion = Congestion()

    def add_connection(self, connection):
        self.congestion += connection.congestion

class Meta_connection:
    def __init__(self, from_op, to_op):
        self.trains = 0
        self.load = 0
        self.from_op = from_op
        self.to_op = to_op

    def add_connection(self, connection):
        self.trains += connection.trains
        self.load += connection.load


class Meta_operating_point:
    def __init__(self, points):
        assert(len(points) > 0)
        self.congestion = sum([p.congestion for p in points],
                Congestion())
        self.gps = np.average([np.array(p.gps) for p in points],axis=0)
        self.connections_outbound = []

        #TODO smarter way to assing id
        self.id_word = points[0].id_word 
        self.id_index = points[0].id_index
        
    def add_connection(self, meta_connection):
        self.connections_outbound.append(meta_connection)

    #TODO maybe store inner throughput
    def add_inner_connection(self, connection):
        pass

    def add_inner_connection_congestion(self, connection):
        self.congestion += connection.congestion   


points_to_meta = {}
connections_to_meta = {}

def cluster_points(x_coords, y_coords, level, cells_per_axis=20):
    assert(len(x_coords) == len(y_coords))
    n_pts = len(x_coords)
    x_min = min(x_coords)
    y_min = min(y_coords)
    x_max = max(x_coords)
    y_max = max(y_coords)
    cell_x = (x_max - x_min) / cells_per_axis
    cell_y = (y_max - y_min) / cells_per_axis
    cells = [[[] for i in range(cells_per_axis)] \
            for j in range(cells_per_axis)]
    for i in range(n_pts):
        x, y = x_coords[i], y_coords[i]
        xc = int((x - x_min) / cell_x)
        yc = int((y - y_min) / cell_y)
        xc = min(xc, cells_per_axis - 1)
        yc = min(yc, cells_per_axis - 1)
        cells[yc][xc].append(i)

    clusters = []
    for yc in range(cells_per_axis):
        for xc in range(cells_per_axis):
            if len(cells[yc][xc]) > 0:
                clusters.append(cells[yc][xc])

    return clusters
    

def coarse(points, connection_congestions, level):
    points = [p for p in points if p.gps[0] != 0]

    #points = points_dict.values()
    x_coords = [p.gps[0] for p in points]
    y_coords = [p.gps[1] for p in points]
    clusters = cluster_points(x_coords, y_coords, level)
    print(f"# of clusters = {len(clusters)}")
    print(len(points))
    print(sum([len(c) for c in clusters]))

    point_to_meta = {}
    for ci, cluster in enumerate(clusters):
        for pi in cluster:
            point_to_meta[points[pi].id_word] = ci
    meta_points = []
    for cluster in clusters:
        meta_points.append(Meta_operating_point(
            [points[i] for i in cluster]))
    
    meta_edges = {}
    for point in points:
        for connection in point.connections_outbound:
            meta1 = point_to_meta[point.id_word]
            if connection.to_op not in point_to_meta:
                continue
            meta2 = point_to_meta[connection.to_op]                    
            if meta1 == meta2:
                meta_points[meta1].add_inner_connection(connection)
            else:
                meta1, meta2 = sorted([meta1, meta2])
                meta_edges.setdefault((meta1, meta2),
                        Meta_connection(meta_points[meta1].id_word,
                            meta_points[meta2].id_word))
                meta_points[meta1].add_connection(meta_edges[(meta1, meta2)])
                meta_edges[(meta1, meta2)].add_connection(connection)

    meta_connection_congestions_dict = {}
    for connection in connection_congestions:
        meta1 = point_to_meta[connection.smaller_op]
        meta2 = point_to_meta[connection.greater_op]                    
        if meta1 == meta2:
            meta_points[meta1].add_inner_connection_congestion(connection)
        else:
            meta_connection_congestions_dict.setdefault(
                    (connection.smaller_op, connection.greater_op),
                    Meta_connection_congestion()
                    )
            meta_connection_congestion[
                    (connection.smaller_op, connection.greater_op)] \
                        .add_connection(connection)


    meta_points_dict = {}
    for p in meta_points:
        meta_points_dict[p.id_word] = p
    return meta_points_dict, meta_connection_congestions_dict 