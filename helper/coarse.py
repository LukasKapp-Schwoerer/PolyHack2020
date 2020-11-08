import numpy as np
import helper.data_extraction
from queue import LifoQueue

class Meta_connection_congestion:
    def __init__(self, op1, op2):
        self.congestion = helper.data_extraction.Congestion()
        op1, op2 = sorted([op1, op2])
        self.smaller_op = op1
        self.greater_op = op2

    def add_connection(self, connection):
        self.congestion += connection.congestion

class Meta_connection:
    def __init__(self, from_op, to_op):
        self.trains = 0
        self.load = 0
        self.from_op = from_op
        self.to_op = to_op
        self.train_type = 'PERSONENVERKEHR'

    def add_connection(self, connection):
        self.trains += connection.trains
        self.load += connection.load


class Meta_operating_point:
    def __init__(self, points):
        assert(len(points) > 0)
        self.congestion = sum([p.congestion for p in points],
                helper.data_extraction.Congestion())
        self.gps = np.average([np.array(p.gps) for p in points],axis=0)
        self.connections_outbound = []
        self.connections_inbound = []

        #TODO smarter way to assing id
        self.id_word = points[0].id_word 
        self.id_index = points[0].id_index
        
        #TODO
        #self.trains = sum([p.trains for p in points])
        
    def add_connection(self, meta_connection):
        self.connections_outbound.append(meta_connection)
    def add_reverse_connection(self, meta_connection):
        self.connections_inbound.append(meta_connection)

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

def cluster_connected(points):
    pdict = {}
    for i, p in enumerate(points):
        pdict[p.id_word] = i

    cur_cluster = 0
    q = LifoQueue()
    clusters = [-1] * len(points)
    for i, sp in enumerate(points):
        if clusters[i] == -1:
            q.put(i)
            while not q.empty():
                cur = q.get()
                clusters[cur] = cur_cluster
                nxts = [conn.to_op for conn in \
                        points[cur].connections_outbound] \
                        + [conn.from_op for conn in \
                        points[cur].connections_inbound]
                for nxt in nxts:
                    if nxt not in pdict:
                        continue
                    ni = pdict[nxt]
                    if clusters[ni] != -1:
                        continue
                    q.put(ni)
            cur_cluster += 1
    #print(f"p {len(points)} cl {cur_cluster}")

    clst = [[] for i in range(cur_cluster)]
    for i in range(len(points)):
        clst[clusters[i]].append(i)
    return clst

def sep_non_connected(points, clusters):
    new_clusters = []
    for cluster in clusters:
        #print(f"clust: {cluster}")
        subclust = cluster_connected([points[i] for i in cluster])
        #print(f"    subclust: {subclust}")
        for new_cl in subclust:
            for ind in range(len(new_cl)):
                new_cl[ind] = cluster[new_cl[ind]]
        #print(f"new subclust: {subclust}")
        new_clusters += subclust
    return new_clusters
    


def coarse(points, connection_congestions, level=1):
    points = [p for p in points if p.gps[0] != 0]
  
    #points = points_dict.values()
    x_coords = [p.gps[0] for p in points]
    y_coords = [p.gps[1] for p in points]
    #clusters = cluster_points(x_coords, y_coords, level)
    clusters = cluster_points(x_coords, y_coords, level, cells_per_axis=8)
    clusters = sep_non_connected(points, clusters)

    print(f"# of clusters = {len(clusters)}")
    #print(len(points))
    #print(sum([len(c) for c in clusters]))

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
                meta_points[meta2].add_reverse_connection(meta_edges[(meta1, meta2)])
                meta_edges[(meta1, meta2)].add_connection(connection)

    meta_connection_congestions_dict = {}
    meta_vcg = {}
    print(f"num of cc={len(connection_congestions)}")
    for connection in connection_congestions:
        if connection.smaller_op not in point_to_meta \
                or connection.greater_op not in point_to_meta:
            continue
            #pass
        meta1 = point_to_meta[connection.smaller_op]
        meta2 = point_to_meta[connection.greater_op]                    
        meta_vcg.setdefault(meta_points[meta1].id_word, \
                meta_points[meta1])
        meta_vcg.setdefault(meta_points[meta2].id_word, \
                meta_points[meta2])
        if meta1 == meta2:
            meta_points[meta1].add_inner_connection_congestion(connection)
        else:
            meta_connection_congestions_dict.setdefault(
                    (meta_points[meta1].id_word, meta_points[meta2].id_word),
                    Meta_connection_congestion(meta_points[meta1].id_word,\
                            meta_points[meta2].id_word)
                    )
            meta_connection_congestions_dict[
                    (meta_points[meta1].id_word, meta_points[meta2].id_word)] \
                        .add_connection(connection)

    ccgs = [ccg for ccg in list(meta_connection_congestions_dict.values())]
    print(f"num of ccgs={len(ccgs)}")


    meta_points_dict = {}
    for p in meta_points:
        meta_points_dict[p.id_word] = p

    return meta_points_dict, list(meta_vcg.values()), ccgs
             
