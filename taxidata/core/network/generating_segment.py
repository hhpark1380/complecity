import numpy as np
import matplotlib.pylab as plt
import math
import time
import networkx as nx
Seoul = np.load('./data_roadAndTaxi/SeoulConvertEdgelist.npy')
Seoul['EDGE'] = np.arange(len(Seoul)) # edge 라벨 재설정(방향이 다른 경우 같으 라벨링이 되어있어서)
node_Seoul = np.unique(Seoul['START_NODE']) # node 집합
"""
define function
"""
def turning_angle(v1,v2):
    magnitudeProduct = np.linalg.norm(v1)*np.linalg.norm(v2)
    angle_innerProduct = math.acos(np.dot(v1,v2)/(magnitudeProduct+9e-12))
    angle_vectorProduct = math.asin(np.cross(v1,v2)/magnitudeProduct)
    if angle_vectorProduct == 0: angle = angle_innerProduct
    else: angle = angle_vectorProduct/abs(angle_vectorProduct)*angle_innerProduct
    return angle

def next_node(input):
    index_find = [k for k, x in enumerate(input[0]) if x == "+"][-1]
    next_edge = Seoul[np.where(Seoul['START_NODE']==int(input[0][(index_find+1):]))]
    a=[]
    for i in range(len(next_edge)):
        a.append(input)
    b=[]
    for n in range(len(next_edge)):
        turning_angle=0
        # turning angle measure
        if input[0].count('+') >= 2:
            cal_turningAg = input[0].split('+')[1:]
            if len(cal_turningAg)>1:
                X_1, Y_1 = Seoul[np.where(Seoul['START_NODE']==int(cal_turningAg[-2]))][0][0],Seoul[np.where(Seoul['START_NODE']==int(cal_turningAg[-2]))][0][1]
                X_2, Y_2 = Seoul[np.where(Seoul['START_NODE']==int(cal_turningAg[-1]))][0][0], Seoul[np.where(Seoul['START_NODE']==int(cal_turningAg[-1]))][0][1]
                X_3, Y_3 = Seoul[np.where(Seoul['START_NODE']==next_edge['END_NODE'][n])][0][0], Seoul[np.where(Seoul['START_NODE']==next_edge['END_NODE'][n])][0][1]
                r1 = np.array([X_2-X_1, Y_2-Y_1])
                r2 = np.array([X_3-X_2, Y_3-Y_2])
                turningAngle = turning_angle(r1,r2)
            if turningAngle==np.pi and a[n][2]<0: turningAngle*=-1
        b.append([a[n][0] + "+" + str(next_edge['END_NODE'][n]), a[n][1] + next_edge['LENGTH'][n],a[n][2]+turning_angle])
    return b

def node_cycle(input):
    output=[]
    for i in range(len(input)):
        output = output + next_node(input[i])
    return output
"""
main
"""
k = 300 # k=300m
segment_int = [] # segment set
for SN in node_Seoul[1000:1001]:
    segmnet=[]
    start = time.time()
    #[+node+node+..., total_length, turning_angle]
    input=[["+" + str(SN), 0, 0]]
    count=0
    while count < 100 :
        input = node_cycle(input)
        pop_parameter=0
        for i in range(len(input)):
            i-=pop_parameter
            check_turnBack = input[i][0].split('+')
            # if path's length exceed k
            if input[i][-2]>k:
                segment.append(input[i])
                input.pop(i)
                pop_parameter+=1
            # if turning angle exceed 2pi
            elif abs(input[i][-1])>2*np.pi:
                segment.append(input[i])
                input.pop(i)
                pop_parameter+=1
        count += 1
        if len(input) == 0: break
    # string -> npy
    # segment_int = []
    for i in range(len(segment)):
        path_str = segment[i][0].split('+')[1:]
        path = []
        for j in range(len(path_str)):
            path.append(int(path_str[j]))
        segment_int.append(path)
    print("time :", time.time() - start)