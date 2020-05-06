import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt
import osmnx as ox
import numpy as np
import shapely.geometry as geom
import h5py as h5

class segment:
    def __init__(self, edge = None):
        if edge is None:
            #Do nothing
            pass
        else:
            #initialize with given node as segment
            self.start_node = edge[0]
            self.num = 1
            self.path = np.array(edge[1:3],dtype = [('node','i4'),('id','i4')])
            self.past_node = self.start_node
            self.last_node = edge[1]
            self.length = edge[-1]['length']
            self.angle = edge[-1]['angle']
            self.edgelist = {edge[:3]:True}
            self.total_angle  = np.array([0],dtype = np.float32)

    def expand(self, edge):
        '''return copy of segment appending extra edge '''
        temp = segment()
        temp.start_node = self.start_node
        temp.past_node = edge[0]
        temp.last_node = edge[1]
        temp.num = self.num+1
        temp.path = np.empty([temp.num],dtype = [('node','i4'),('id','i4')])
        temp.path[:-1] = self.path
        temp.path[-1] = edge[1:3]
        temp.length = self.length + edge[-1]['length']
        temp.angle =  edge[-1]['angle']
        temp.edgelist = {edge[:3]:True}
        for e in self.edgelist:
            temp.edgelist[e] = True
        temp.total_angle = np.zeros([temp.num],dtype = np.float32)
        temp.total_angle[:-1] = self.total_angle + temp.angle- self.angle
        return temp

    def check(self, k):
        '''check condition of k segments'''
        return self.length> k or self.total_angle[-1]<-2*np.pi or self.total_angle[-1]>2*np.pi #(self.total_angle <-2*np.pi).any() or (self.total_angle > 2*np.pi).any()

    def overlap(self, edge):
        '''check overlap with given edge'''
        if self.num == 1:
            return False
        return edge[:3] in self.edgelist

    def __repr__(self):
        return "<segment from node '{}' to '{}', total num : {}>".format(self.start_node, self.last_node, self.num)

    def __lt__(self, other):
        '''sorting'''
        return self.length<other.length

    def __gt__(self, other):
        '''sorting'''
        return self.length>other.length

    def __le__(self, other):
        '''sorting'''
        return self.length<=other.length

    def __ge__(self, other):
        '''sorting'''
        return self.length>=other.length

    def edges(self):
        '''return edgelist'''
        e = []
        temp = self.start_node
        for p in self.path:
            e.append((temp,p['node'],p['id']))
            temp = p['node']
        return e

    def nodes(self):
        '''return node list'''
        n = [self.start_node]
        if self.num == 1:
            n.append(self.path['node'])
            return n
        for p in self.path:
            n.append(p['node'])
        return n

    def plot(self, pos, *arg,**kwarg):
        '''plot segment in aspect of graph'''
        temp = nx.path_graph(self.num+1,create_using=nx.DiGraph)
        position = {}
        for i,n in enumerate(self.nodes()):
            position[i] = pos[n]
        nx.draw(temp, position, *arg, **kwarg)

    def stitch_score(self, other):
        pass


def k_segments(G, node, k= 100):
    '''k_segments with only breadth-first searching'''
    segments = [segment(edge) for edge in G.edges(node,keys = True, data = True)]
    k_segments = []
    iter_num  = 0
    while segments:
        iter_num += 1
        target = segments.pop(0)
        ch = False
        #print("target : {},{}".format(target.past_node, target.last_node))
        for edge in G.edges(target.last_node, keys = True, data = True):
            if edge[1] == target.past_node or target.overlap(edge): continue
            #print("to : {}, {}".format(edge[0], edge[1]))
            ch = True
            temp = target.expand(edge)
            if temp.check(k):
                k_segments.append(temp)
            else:
                segments.append(temp)
        if not ch:
            k_segments.append(target)
        if iter_num == 1e5:
            print(node)
        #print(k_segments)
    return k_segments

def k_segments_strict_bfs(G, node, k= 100):
    '''no overlapping node'''
    segments = [segment(edge) for edge in G.edges(node,keys = True, data = True)]
    k_segments = []
    nodes = {node :True}
    iter_num  = 0
    while segments:
        iter_num += 1
        target = segments.pop(0)
        ch = False
        #print("target : {},{}".format(target.past_node, target.last_node))
        for edge in G.edges(target.last_node, keys = True, data = True):
            if edge[1] in nodes: continue
            #print("to : {}, {}".format(edge[0], edge[1]))
            ch = True
            nodes[edge[1]] = True
            temp = target.expand(edge)
            if temp.check(k):
                k_segments.append(temp)
            else:
                segments.append(temp)
        #if not ch:
            #k_segments.append(target)
        if iter_num == 1e5:
            print(node)
        #print(k_segments)
    return k_segments

def k_segments_strict_bfs_with_length(G, node, k= 100):
    '''no overlapping node and search with length.'''
    segments = [segment(edge) for edge in G.edges(node,keys = True, data = True)]
    k_segments = []
    nodes = {node :True}
    iter_num  = 0
    segments.sort()
    while segments:
        iter_num += 1
        target = segments.pop(0)
        ch = False
        #print("target : {},{}".format(target.past_node, target.last_node))
        for edge in G.edges(target.last_node, keys = True, data = True):
            if edge[1] in nodes: continue
            #print("to : {}, {}".format(edge[0], edge[1]))
            ch = True
            nodes[edge[1]] = True
            temp = target.expand(edge)
            if temp.check(k):
                k_segments.append(temp)
            else:
                segments.append(temp)
        if not ch:
            k_segments.append(target)
        if iter_num == 1e5:
            print(node)
        #print(k_segments)
        segments.sort()
    return k_segments

def k_segments_semi_strict_bfs(G, node, k= 100):
    '''no overlap within single segment.'''
    segments = [segment(edge) for edge in G.edges(node,keys = True, data = True)]
    k_segments = []
    nodes = {node :True}
    iter_num  = 0
    while segments:
        iter_num += 1
        target = segments.pop(0)
        ch = False
        #print("target : {},{}".format(target.past_node, target.last_node))
        for edge in G.edges(target.last_node, keys = True, data = True):
            if edge[1] in target.nodes(): continue
            #print("to : {}, {}".format(edge[0], edge[1]))
            ch = True
            nodes[edge[1]] = True
            temp = target.expand(edge)
            if temp.check(k):
                k_segments.append(temp)
            else:
                segments.append(temp)
        #if not ch:
            #k_segments.append(target)
        if iter_num == 1e5:
            print(node)
        #print(k_segments)
    return k_segments
