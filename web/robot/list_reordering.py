import sys
import math

#Finds the closest point from the given point
def min_dist_point(start, remaininglist):

    # Initialize minimum distance to max val and null for minimal point
    min_dist = sys.maxsize
    min_point = None

    # Search for nearest point if distance is smaller than previous
    #then keep that point
    for v in remaininglist:
        dist = euclidean_distance(start, v)
        if dist < min_dist:
            min_dist = dist
            min_point = v

    return min_point

#Finds Euclidean Distance Given Two Points
def euclidean_distance(start, end):
    return math.sqrt((start[0] - end[0])**2 +(start[1] - end[1])**2)

#Returns an ordered list from an unordered list
def reorder(list):

    #Starts with first item in list.
    current = list[0]
    ordered_list = [current]
    list.remove(current)
    
    #Once added to the ordered list, it removes from previous list
    while len(list) != 0:
        closest = min_dist_point(current, list)
        list.remove(closest)
        ordered_list.append(closest)
        current = closest

    return ordered_list