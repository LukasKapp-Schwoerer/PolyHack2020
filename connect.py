import numpy as np
from numpy.linalg import norm
from queue import LifoQueue
from disjoint_set import DisjointSet

class Connection:
    def __init__(self, from_op, to_op, trains, load, train_type):
        self.from_op = from_op
        self.to_op = to_op
        self.trains = trains
        self.load = load
        self.train_type = train_type

    def __str__(self):
        return f"{self.from_op} {self.to_op} {self.trains} {self.load}"

def connect(points_dict):
    points = list(points_dict.values())

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

    clst = [[] for i in range(cur_cluster)]
    for i in range(len(points)):
        clst[clusters[i]].append(i)
        
   
    print(f"clust: {len(clst)}")
    print(f"{len(points)} ? {sum([len(c) for c in clst])}")       

    ds = DisjointSet()
    for c1 in range(len(clst)):
        min_dist = np.inf
        best_i1 = 0
        best_i2 = 0
        best_c2 = 0
        for i1 in clst[c1]:
            for c2 in range(len(clst)):
                if not ds.connected(c1, c2):
                    for i2 in clst[c2]:
                        dist = norm(np.array(points[i1].gps) \
                                    - np.array(points[i2].gps))
                        if (dist < min_dist):
                            min_dist = dist
                            best_i1 = i1
                            best_i2 = i2
                            best_c2 = c2

        if min_dist != np.inf:
            ds.union(c1, best_c2)
            conn = Connection(points[best_i1].id_word, 
                    points[best_i2].id_word,
                    0, 0, "dummy")
            points[best_i1].connections_outbound.append(conn)
            points[best_i2].connections_inbound.append(conn)
        else:
            pass
            #print("wtf")
