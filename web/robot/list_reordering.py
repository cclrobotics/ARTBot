import sys
import math
import random

class Point():
    def __init__(self, x, y):
        self.x = x;
        self.y = y;

    def __eq__(self, other):
        return (self.x == other.x) & (self.y == other.y)


def minDistance(start, remaininglist):

        # Initilaize minimum distance for next node
    min = sys.maxsize

        # Search not nearest vertex not in the
        # shortest path tree
    for v in remaininglist:
        dist = euclideanDistance(start, v)
        if dist < min:
            min = dist
            min_point = v

    return min_point

def euclideanDistance(start, end):
    return math.sqrt((start[0] - end[0])**2 +(start[1] - end[1])**2)



    # Funtion that implements Dijkstra's single source
    # shortest path algorithm for a graph represented
    # using adjacency matrix representation
def dijkstra_altered(list):

    current = list[0]
    ordered_list = [current]
    list.remove(current)
    while len(list) != 0:
        closest = minDistance(current, list)
        list.remove(closest)
        ordered_list.append(closest)
        current = closest
    return ordered_list

test_list = []
Starter = [1, 1]
test_list.append(Starter)
for i in range(0,9):
    test_list.append([random.randint(1,100), random.randint(1,100)])
endlist = dijkstra_altered(test_list);
print("End")
