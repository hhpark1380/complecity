import numpy as np
import networkx as nx
import os
import re
import matplotlib.pyplot as plt

# edgelist, speed data convert to npy
# def conver2npy_edgelist(path,filename):
#     data = np.genfromtxt(path, delimiter=',',skip_header=1,dtype=[('Link', 'int'), ('Node_Start', 'int'), ('Longitude_Start', 'float'),('Latitude_Start', 'float'),('Node_End', 'int'), ('Longitude_End', 'float'),('Latitude_End', 'float'),('LENGTH', 'float')])
#     np.save(filename,data)
# def convert2npy_linkspeed(path):
#     path_dr = path
#     file_list = os.listdir(path_dr)
#     file_list.sort()
#     re_file_list = file_list[5:len((file_list))]
#     for path_file in re_file_list:
#         data = np.genfromtxt(path_file,delimiter=',',skip_header=1, dtype=[('Period','U12'),('Link','int'),('Speed','float')])
#         filename=int(re.findall('\d+',path_file)[0])
#         np.save('{}.npy'.format(filename),data)

# generate Street network
def genStreetNet(Edgelist):
    # node label & number
    node_list = np.unique(Edgelist['Node_Start'])
    # network generating
    G = nx.DiGraph()
    # add nodes
    G.add_nodes_from(node_list)
    # add edges
    for i in range(len(Edgelist)):
        G.add_edge(Edgelist['Node_Start'][i],Edgelist['Node_End'][i],label=Edgelist['Link'][i])
    return G

# generate newowrk nodes' position
def network_pos(Edgelist):
    # assign pos for nodes
    return {i:[Edgelist[Edgelist['Node_Start']==i]['Longitude_Start'][0],Edgelist[Edgelist['Node_Start']==i]['Latitude_Start'][0]]for i in range(len(np.unique(Edgelist['Node_Start'])))}

# get max velocity each street link
def Max_velocity(velocity0,velocity1):
    max_velo = np.zeros(len(np.unique(velocity0['Link'])))
    for i in range(len(max_velo)):
        max_velo[i] = max([max(velocity0[velocity0['Link'] == i+1]['Speed']),max(velocity1[velocity1['Link'] == i+1]['Speed'])])
    return max_velo

# get relative velocity
def relativeVelocity(Period,velocity0,velocity1):
    return np.array(velocity0[velocity0['Period']==Period]['Speed']/Max_velocity(velocity0,velocity1))

# generate network given weight by relative speed
def genStreetNet_speed(Edgelist,reVelo):
    # node label & number
    node_list = np.unique(Edgelist['Node_Start'])
    # network generating
    G = nx.DiGraph()
    # add nodes
    G.add_nodes_from(node_list)
    # add edges
    for i in range(len(Edgelist)):
        G.add_edge(Edgelist['Node_Start'][i],Edgelist['Node_End'][i],label=Edgelist['Link'][i],weight=reVelo[i])
    return G
# remove link under parameter q
def remove_qRoad(q,Edgelist,reVelo):
    orign_net = genStreetNet_speed(Edgelist,reVelo)
    return_net = genStreetNet_speed(Edgelist,reVelo)
    Edge = np.array(orign_net.edges)
    for i in range(len(Edge)):
        if list(orign_net.edges.data('weight'))[i][2] < q:
            return_net.remove_edge(*Edge[i])
    return return_net

# get weakly connected components
def weaklycc(network):
    return [len(c) for c in sorted(nx.weakly_connected_components(network), key=len, reverse=True)]

# measuring GCC, SCC, CPoint, and generating graph
def criticalGraph(Period,edgelist,speedlist0,speedlist1):
    # relative velocity
    rv = relativeVelocity(Period,speedlist0,speedlist1)
    # get GCC, SCC each q
    h = 101
    cc = np.zeros([2,h])
    # control parameter q
    q,a = np.linspace(0,1,h),0
    for i in q:
        dist=weaklycc(remove_qRoad(i,edgelist,rv))
        cc[0,a] = dist[0]
        if len(dist)>=2:cc[1,a]=dist[1]
        a+=1
    # get critical point(SCC max size)
    criticalPoint=q[np.where(cc[1]==max(cc[1]))][0]
    # Graph
    fig, ax1 = plt.subplots(figsize=(12,9))
    ax2 = ax1.twinx()
    curve1 = ax1.errorbar(q,cc[0]/1902,marker='s',markersize=20,label='GCC')
    curve2 = ax2.errorbar(q,cc[1]/1902,marker='^',markersize=20,label='SCC',c='orange')
    curves=[curve1,curve2]
    ax1.legend(curves,[curve.get_label()for curve in curves],fontsize='x-large')
    plt.savefig('Chengdu_june1_{}_ciritcalpoint_{}.png'.format(Period,criticalPoint),transparent=True,dpi=300)
    plt.close()
