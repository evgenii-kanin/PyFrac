import numpy as np
import matplotlib.pyplot as plt
from level_set import *


def find_indexes_repeatd_elements(arr):
    """
          0  1  2  3  4  5  6  7
    arr=[10,15,33,33,18,22,16,22]
    return all indexes of repeated elements [2,3,5,7]
    """
    sort_indexes = np.argsort(arr)
    arr = np.asarray(arr)[sort_indexes]
    vals, first_indexes,  counts = np.unique(arr,
        return_index=True, return_counts=True)
    indexes = np.split(sort_indexes, first_indexes[1:])
    for x in indexes:
        x.sort()
    duplicates_positions_in_indexes = np.where(counts > 1)[0]
    if duplicates_positions_in_indexes.size > 0 :
        indexes_of_all_repeated = itertools_chain_from_iterable([indexes[j] for j in np.where(counts > 1)[0]])
        return indexes_of_all_repeated
    else: return []

class Point:
    # Define the object point
    def __init__(self,name,x,y):
        self.name = name
        self.x = x
        self.y = y

def distance(p1, p2):
    # USING OBJECTS: POINT
    #
    # Compute the euclidean distance between two points
    return np.sqrt((-p1.x + p2.x)**2 + (-p1.y + p2.y)**2)

def copute_area_of_a_closed_front(xintersection,yintersection):
    # todo: remove for speed
    if  xintersection.size !=  yintersection.size : raise SystemExit('ERROR: bad coordinate sizes')

    # use the Shoelace formula (Gauss area formula or surveyor's formula) to compute the area of a polygon
    # Performed tests:
    # copute_area_of_a_closed_front(np.asarray([0,1,0]),np.asarray([0,0,1])) == 0.5
    # copute_area_of_a_closed_front(np.asarray([1,38,9]),np.asarray([2,2,20])) == 333
    # copute_area_of_a_closed_front(np.asarray([0,2,3,0.5]),np.asarray([0,0,3,3])) == 6.75

    n = xintersection.size
    area = \
        np.abs( np.dot(xintersection[0:n-1],yintersection[1:n]) \
                     + xintersection[n-1] * yintersection[0] \
              - np.dot(xintersection[1:n],  yintersection[0:(n-1)]) \
                     - xintersection[0]   * yintersection[n-1])/2.
    return area

def pointtolinedistance(p1, p2, p0):
    # USING OBJECTS: POINT
    #
    # Compute the minimum distance from a point of coordinates (x0,y0) to a the line passing through 2 points.
    # The function works only for planar problems.
    x0, x1, x2 = [p0.x, p1.x, p2.x]
    y0, y1, y2 = [p0.y, p1.y, p2.y]
    mac_precision = 10 * np.finfo(float).eps
    dist=0
    if np.abs(x2 - x1)/np.maximum(np.abs(x2),np.abs(x1)) < mac_precision:  # the front is a vertical line
        dist=np.abs(x0 - x1)
    elif np.abs(y2 - y1)/np.maximum(np.abs(y2),np.abs(y1)) < mac_precision:  # the front is an horizontal line
        dist = np.abs(y0 - y1)
    else: #general case
        dist = np.abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1)/distance(p1, p2)
    return dist

def elements(typeindex, nodeindex, connectivityedgeselem, Connectivitynodeselem, edgeORvertexID):
    # This function returns in the case:
    #  a) -> two element names <=> NODE ON EDGE
    #  b) -> four element names  <=> NODE ON VERTEX
    #
    #
    # CASE a)
    if typeindex[nodeindex] == 0:  # the node is one the edge of a cell
        cellOfNodei = connectivityedgeselem[edgeORvertexID[nodeindex]]
    # CASE b)
    else: # the node is one vertex of a cell
        cellOfNodei = Connectivitynodeselem[edgeORvertexID[nodeindex]]
    return cellOfNodei

def findcommon(nodeindex0, nodeindex1, typeindex, connectivityedgeselem, Connectivitynodeselem, edgeORvertexID):
    """
    Given two points we return the cells that are in common between them

    :param nodeindex0: position of the node 0 inside the list of the found intersections that defines the front
    :param nodeindex1: position of the node 1 inside the list of the found intersections that defines the front
    :param typeindex: array that specify if a node at the front is an existing vertex or an intersection with the edge
    :param connectivityedgeselem: given an edge number, it will return all the elements that have the given edge
    :param Connectivitynodeselem: given a node number, it will return all the elements that have the given node
    :param edgeORvertexID: list that contains for each node at the front the number of the vertex or of the edge where it lies
    :return: list of elements
    """
    cellOfNodei = elements(typeindex, nodeindex0, connectivityedgeselem, Connectivitynodeselem, edgeORvertexID)
    cellOfNodeip1 = elements(typeindex, nodeindex1, connectivityedgeselem, Connectivitynodeselem, edgeORvertexID)
    diff = np.setdiff1d(cellOfNodei,cellOfNodeip1)  # Return the unique values in cellOfNodei that are not in cellOfNodeip1.
    common = np.setdiff1d(cellOfNodei, diff)  # Return the unique values in cellOfNodei that are not in diff.
    return common

def filltable(nodeVScommonelementtable, nodeindex, common, sgndDist_k, column):
    # we define a node as the intersection between the zero of the level set and the grid made of elements
    # given two elements, this function returns the common element/elements between two nodes that are supposed to
    # be one after the other along the 

    if len(common) == 1:
        nodeVScommonelementtable[nodeindex, column]=common[0]
        exitstatus = True
    elif len(common) > 1:
        """
        situations with two common elements:
           |      |                  |      |           |      |
        ___|______|____           ___|_*__*_|____    ___|_*____*____
           |      |                  |/    \|           |/     |\        
        ___*______*____           ___/______\____    ___/______|_\__
           |      |                 /|      |\         /|      |  \  
        ___|______|____           _/_|______|_\___   _/_|______|___\___
           |      |                  |      |           |      |
        In this situation take the i with LS<0 as tip
        (...if you choose LS>0 as tip you will not find zero vertexes then...)
        """
        #nodeVScommonelementtable[nodeindex, column] = common[np.argmax(sgndDist_k[common])]
        nodeVScommonelementtable[nodeindex,column]=common[np.argmin(sgndDist_k[common])]
        exitstatus = True
    elif len(common) == 0:
        #raise SystemExit('ERROR: two consecutive nodes does not belongs to a common cell')
        exitstatus = False
    return nodeVScommonelementtable, exitstatus

def ISinsideFracture(i,mesh,sgndDist_k):
    """
    you are in cell i
    you want to know if points 0,1,2,3 are inside or outside of the fracture
    -extrapolate the level set at those points by taking the level set (LS) at the center of the neighbors cells
    -if at the point the LS is < 0 then the point is inside
      _   _   _   _   _   _
    | _ | _ | _ | _ | _ | _ |
    | _ | _ | _ | _ | _ | _ |
    | _ | e | a | f | _ | _ |
    | _ | _ 3 _ 2 _ | _ | _ |
    | _ | d | i | b | _ | _ |
    | _ | _ 0 _ 1 _ | _ | _ |
    | _ | h | c | g | _ | _ |
    | _ | _ | _ | _ | _ | _ |
    """
    #                         0     1      2      3
    #       NeiElements[i]->[left, right, bottom, up]
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]

    a = mesh.NeiElements[i, top_elem]
    b = mesh.NeiElements[i, right_elem]
    c = mesh.NeiElements[i, bottom_elem]
    d = mesh.NeiElements[i, left_elem]
    e = mesh.NeiElements[d, top_elem]
    f = mesh.NeiElements[b, top_elem]
    g = mesh.NeiElements[b, bottom_elem]
    h = mesh.NeiElements[d, bottom_elem]

    hcid_mean = np.mean(np.asarray(sgndDist_k[[h, c, i, d]]))
    cgbi_mean = np.mean(np.asarray(sgndDist_k[[c, g, b, i]]))
    ibfa_mean = np.mean(np.asarray(sgndDist_k[[i, b, f, a]]))
    diae_mean = np.mean(np.asarray(sgndDist_k[[d, i, a, e]]))
    answer_on_vertexes = [hcid_mean<0, cgbi_mean<0, ibfa_mean<0, diae_mean<0]
    return answer_on_vertexes

def findangle(x1, y1, x2, y2, x0, y0):
    """
    Compute the angle with respect to the horizontal direction between the segment from a point of coordinates (x0,y0)
    and orthogonal to a the line passing through 2 points. The function works only for planar problems.

    Args:
    :param x0: coordinate x point
    :param y0: coordinate y first
    :param x1: coordinate x first point that defines the line
    :param y1: coordinate y first point that defines the line
    :param x2: coordinate x second point that defines the line
    :param y2: coordinate y second point that defines the line

    Returns:
    :return: angle, xintersections, yintersections

    """
    mac_precision = 10*np.finfo(float).eps
    if np.abs(x2 - x1)/np.maximum(np.abs(x2),np.abs(x1)) < mac_precision:  # the front is a vertical line
        x = x2
        y = y0
        angle = 0.
    elif np.abs(y2 - y1)/np.maximum(np.abs(y2),np.abs(y1)) < mac_precision:  # the front is an horizontal line
        angle = np.pi/2
        x = x0
        y = y2
    else:
        # m and q1 are the coefficients of the line defined by (x1,y1) and (x2,y2): y = m * x + q1
        # q2 is the coefficients of the line defined by (x,y) and (x0,y0): y = -1/m * x + q2
        m = (y2 - y1) / (x2 - x1)
        q1 = y2 - m * x2
        q2 = y0 + x0 / m
        x = (q2 - q1) * m / (m * m + 1)
        y = m * x + q1
        angle = np.arctan(np.abs((y-y0))/np.abs((x-x0)))

    return angle, x, y

def plot_xy_points(anularegion, mesh, sgndDist_k, Ribbon, x,y, fig=None):
        #fig = None
        if fig is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            A = np.full(mesh.NumberOfElts, np.nan)
            A[anularegion] = sgndDist_k[anularegion]
            from visualization import plot_fracture_variable_as_image
            fig = plot_fracture_variable_as_image(A, mesh, fig=fig)
        else:
            ax = fig.get_axes()[0]
        # find positive non ribbon
        nonRibbon = np.setdiff1d(anularegion, Ribbon)
        Positive_nonRibbon = nonRibbon[np.where(sgndDist_k[nonRibbon] > 0)[0]]
        plt.plot(mesh.CenterCoor[Ribbon, 0], mesh.CenterCoor[Ribbon, 1], ".", marker="_", color='g')
        plt.plot(mesh.CenterCoor[Positive_nonRibbon, 0], mesh.CenterCoor[Positive_nonRibbon, 1], ".", marker="+",
                 color='r')
        Negative_nonRibbon = np.setdiff1d(nonRibbon, Positive_nonRibbon)
        if Negative_nonRibbon.size > 0:  # plot them
            plt.plot(mesh.CenterCoor[Negative_nonRibbon, 0], mesh.CenterCoor[Negative_nonRibbon, 1], ".",
                     marker="_", color='b')
        plt.plot(np.asarray(x), np.asarray(y), '.-', color='red')
        x_center =mesh.CenterCoor[anularegion,0]
        y_center = mesh.CenterCoor[anularegion,1]
        for i, txt in enumerate(anularegion):
            ax.annotate(txt, (x_center[i], y_center[i]))
        plt.show()
        return fig

def plot_cells(anularegion,mesh,sgndDist_k, Ribbon,list,fig=None, annotate=False):
    if fig is None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        A = np.full(mesh.NumberOfElts, np.nan)
        A[anularegion] = sgndDist_k[anularegion]
        from visualization import plot_fracture_variable_as_image

        fig = plot_fracture_variable_as_image(A, mesh, fig=fig)
    else:
        ax = fig.get_axes()[0]


    # find positive non ribbon
    nonRibbon = np.setdiff1d(anularegion, Ribbon)
    Positive_nonRibbon = nonRibbon[np.where(sgndDist_k[nonRibbon] > 0)[0]]
    plt.plot(mesh.CenterCoor[Ribbon, 0], mesh.CenterCoor[Ribbon, 1], ".", marker="_", color='g')
    plt.plot(mesh.CenterCoor[Positive_nonRibbon, 0], mesh.CenterCoor[Positive_nonRibbon, 1], ".", marker="+", color='r')
    Negative_nonRibbon = np.setdiff1d(nonRibbon, Positive_nonRibbon)
    if Negative_nonRibbon.size > 0:  # plot them
        plt.plot(mesh.CenterCoor[Negative_nonRibbon, 0], mesh.CenterCoor[Negative_nonRibbon, 1], ".",
                 marker="_", color='b')

    plt.plot(mesh.CenterCoor[list, 0] + mesh.hx * .1,
             mesh.CenterCoor[list, 1] + mesh.hy * .1, ".", color='y')
    if annotate:
        x_center = mesh.CenterCoor[anularegion,0]
        y_center = mesh.CenterCoor[anularegion,1]
        for i, txt in enumerate(anularegion):
            ax.annotate(txt, (x_center[i], y_center[i]))

    plt.show()
    return fig

def get_fictitius_cell_type(LS):
    number_of_negative_cells=np.sum((LS<0).astype(int))
    if number_of_negative_cells == 1:
        return 3
    elif number_of_negative_cells == 3:
        return 4
    else:
        if (LS[0]>0 and LS[2]>0) or (LS[0]<0 and LS[2]<0):
            return 2
        else:
            return 1

def get_fictitius_cell_specific_names(index_to_output,fictitius_cells, NeiElements):
    """
     _ _ _ _ _ _
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|
    |_|_|a|b|_|_|
    |_|_|i|c|_|_|
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|

    for understanding the first operation think that you are in the cell i --> take the cell a,b,c
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                              0     1      2      3
    """
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]

    a = NeiElements[fictitius_cells, top_elem]
    c = NeiElements[fictitius_cells, right_elem]
    b = NeiElements[fictitius_cells + 1, top_elem]

    if index_to_output == "left right":
        m0 = np.column_stack((a,b))
        m1 = np.column_stack((fictitius_cells, c))

    elif index_to_output == "bottom top":
        m0 = np.column_stack((c,b))
        m1 = np.column_stack((fictitius_cells, a))
    return m0,m1

def get_fictitius_cell_names(index_to_output,fictitius_cells, NeiElements):
    """
     _ _ _ _ _ _
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|
    |_|_|a|b|_|_|
    |_|_|i|c|_|_|
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|

    for understanding the first operation think that you are in the cell i --> take the cell a,b,c
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                              0     1      2      3
    """
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]


    a = NeiElements[fictitius_cells, top_elem]
    c = NeiElements[fictitius_cells, right_elem]
    b = NeiElements[fictitius_cells + 1, top_elem]
    full_matrix=np.column_stack((fictitius_cells, c, b, a))
    row_idx=np.arange(0,full_matrix.shape[0],1,dtype=int)
    # very nice peace of code below: I am randoimly specific positions from the matrix
    return full_matrix[[row_idx[None,:],index_to_output.transpose()]]

def get_fictitius_cell_all_names(fictitius_cells, NeiElements):
    """
     _ _ _ _ _ _
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|
    |_|_|a|b|_|_|
    |_|_|i|c|_|_|
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|

    for understanding the first operation think that you are in the cell i --> take the cell a,b,c
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                              0     1      2      3
    """
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]


    a = NeiElements[fictitius_cells, top_elem]
    c = NeiElements[fictitius_cells, right_elem]
    b = NeiElements[c, top_elem]

    return np.column_stack((fictitius_cells, c, b, a))

def get_LS_on_i_fictitius_cell(columns_to_output,fictitius_cells, NeiElements, sgndDist_k):
    """
     _ _ _ _ _ _
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|
    |_|_|a|b|_|_|
    |_|_|i|c|_|_|
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|

    for understanding the first operation think that you are in the cell i --> take the cell a,b,c
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                              0     1      2      3
    """
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]

    if columns_to_output == "icba" or columns_to_output == "iabc" or columns_to_output == "ibca":
        a = NeiElements[fictitius_cells, top_elem]
        c = NeiElements[fictitius_cells, right_elem]
        # when close to the boundary c might be the fictitious cell itself
        b = NeiElements[c, top_elem]

        #creating a matrix with 4 columns: i_cells, c, b, a substituting the value of the signed distance
        return sgndDist_k[np.column_stack((fictitius_cells, c, b, a))]

    elif columns_to_output == "ab" :
        a = NeiElements[fictitius_cells, top_elem]
        c = NeiElements[fictitius_cells, right_elem]
        # when close to the boundary c might be the fictitious cell itself
        b = NeiElements[c, top_elem]

        #creating a matrix with 2 columns: b, a substituting the value of the signed distance
        return sgndDist_k[np.column_stack((a, b))]

    elif columns_to_output == "i" :

        # creating a matrix with 1 columns: i_cells, substituting the value of the signed distance
        return sgndDist_k[fictitius_cells]

def find_fictitius_cells(anularegion, NeiElements, sgndDist_k):
    """
    This function has vectorized operations.
    This function returns a list of "valid" "fictitius cells".
    A fictitius cell is made of 4 cells of the mesh e.g. cells i,a,b,c in the mesh below.
    A fictitius cell is represented by the name of the element in position i in the mesh below
    A valid fictitius cell is a cell where at least one vertex has Level Set<0 and at least one has LS>0
    A valid fictitius cell is important because we know the front is passing through it.
    The front will always enter and exit the fictitius cell from two different edges.
    The front can't exit the fictitious cell from a vertex because we set LS -(machine precision) where it was 0.

     _ _ _ _ _ _
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|
    |_|_|a|b|_|_|
    |_|_|i|c|_|_|
    |_|_|_|_|_|_|
    |_|_|_|_|_|_|

    for understanding the first operation think that you are in the cell i --> take the cell a,b,c
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                              0     1      2      3
    """
    LS = get_LS_on_i_fictitius_cell("icba",anularegion, NeiElements, sgndDist_k)

    """
    Explanation
    
    the following line:
    i_indexes_of_fictitius_cells=np.where(np.column_stack((np.all(LS > 0.,axis=1), np.all(LS < 0.,axis=1))).sum(axis=1) == 0)[0]
    
    is equivalent to:
    1-    condition_1=np.all(LS > 0.,axis=1)  
    2-    condition_2=np.all(LS < 0.,axis=1)
    3-    conditions_1_and_2=np.column_stack((condition_1, condition_2))
    4-    false_for_fictitius_cells=conditions_1_and_2.sum(axis=1)
    5-    i_indexes_of_fictitius_cells=np.where(false_for_fictitius_cells == 0)[0]
    
    that means
    1-   create a vector with True if in a row of LS alla the values are > 0  
    2-   create a vector with True if in a row of LS alla the values are < 0
    3-   create a matrix with the columns defined by the 2 vectors computed above
    4-   for each row sum the True/False of the first column with True/False of the second.
         the possibilities are:
         False + False = False (0)
         False + True  = True  (1)
         True + False  = True  (1)
    5-   Find the indexes of False values, i.e. of the i cells in each valid fictitius cell
    
    NOTE: I am expectin non empty list of fictitius cells        
    """
    i_indexes_of_fictitius_cells = np.where(np.column_stack((np.all(LS > 0.,axis=1), np.all(LS < 0.,axis=1))).sum(axis=1) == 0)[0]

    try:
        if i_indexes_of_fictitius_cells.size < 1:
            raise FileNotFoundError
    except FileNotFoundError:
        print("ERROR: The front does not exist")


    """
        Whe define the fictitius cell types:
    
        type 1        |   type 2        |    type 3       |    type 4
        2(+) & 2(-)   |   2(+) & 2(-)   |    3(+) & 1(-)  |    3(-) & 1(+)  
        + ------ -    |   + ------ -    |    + ------ -   |    - ------ +         
        |        |    |   |        |    |    |        |   |    |        |
        |        |    |   |        |    |    |        |   |    |        |
        + ------ -    |   - ------ +    |    + ------ +   |    - ------ -
        
        With the following lines we want to find the cells of type number 2
     
                    LS_i=LS[i_indexes_of_fictitius_cells,0]
                    LS_c=LS[i_indexes_of_fictitius_cells,1]
                    LS_b=LS[i_indexes_of_fictitius_cells,2]
                    LS_a=LS[i_indexes_of_fictitius_cells,3]
                    
                    LS_i_times_LS_c=np.prod([LS_i, LS_c], axis=0)
                    LS_b_times_LS_a=np.prod([LS_b, LS_a], axis=0)
                    LS_a_times_LS_c=np.prod([LS_a, LS_c], axis=0)
                    LS_b_times_LS_i=np.prod([LS_b,LS_i], axis=0)
                
                    i_indexes_of_TYPE_2_cells = i_indexes_of_fictitius_cells[
                        np.where((LS_i_times_LS_c < 0. +
                                  LS_b_times_LS_a < 0. +
                                  LS_a_times_LS_c > 0. +
                                  LS_b_times_LS_i > 0.) == 4)[0]]
                  
        conceptually we are looking for the cases (if they exist) where two front of the same fracture or two different 
        fractures are crossing the same fictitius cell. We could call these fictitius cells as "double_front_fictitius_cells"
        but we will always coalesce the fractures in these situation, even when they are not.
        We can identify these situations considering the sign of the level set at the vertexes of the fictitius cell
        
        i  c    b  a
        +  -    +  -    is desidered 
        -  +    -  +    is desidered 
        -  +    +  -    is not desidered
        +  -    -  +    is not desidered
        +  +    -  -    is not desidered
        -  -    +  +    is not desidered
        -  -    -  -    is not possible
        +  +    +  +    is not possible
        all the rest    is not desidered
        
        the product between columns should give the following signs:
        
        i*c  b*a  a*c  b*i
         -    -    +    +    is desidered 
         
        some tests are performed on the results: 
        
        i*c  b*a  a*c  b*i
        <0?  <0?  >0?  >0?
         1    1    1    1    True=1, is desidered 
         
        we can summ all the "Trues" and check if the results is a sharp 4.
             
        """

    LS_i=LS[i_indexes_of_fictitius_cells,0]
    LS_c=LS[i_indexes_of_fictitius_cells,1]
    LS_b=LS[i_indexes_of_fictitius_cells,2]
    LS_a=LS[i_indexes_of_fictitius_cells,3]

    LS_i_times_LS_c=np.prod([LS_i, LS_c], axis=0)
    LS_b_times_LS_a=np.prod([LS_b, LS_a], axis=0)
    LS_a_times_LS_c=np.prod([LS_a, LS_c], axis=0)
    LS_b_times_LS_i=np.prod([LS_b,LS_i], axis=0)

    i_indexes_of_TYPE_2_cells = i_indexes_of_fictitius_cells[
        np.where((np.less(LS_i_times_LS_c,0.) +
                  np.less(LS_b_times_LS_a, 0.) +
                  np.greater(LS_a_times_LS_c, 0.) +
                  np.greater(LS_b_times_LS_i, 0.) ) == 4)[0]]

    """
    Whe define the fictitius cell types:
    
    type 1        |   type 2        |    type 3       |    type 4
    2(+) & 2(-)   |   2(+) & 2(-)   |    3(+) & 1(-)  |    3(-) & 1(+)  
    + ------ -    |   + ------ -    |    + ------ -   |    - ------ +         
    |        |    |   |        |    |    |        |   |    |        |
    |        |    |   |        |    |    |        |   |    |        |
    + ------ -    |   - ------ +    |    + ------ +   |    - ------ -
    
    cell type 2 has been recognized just above.
    Now we want to find types 1 and 3
    Remember that:
    type 1 OR 4: 2(+) & 2(-)               ----> the product of the LS on all the vertexes will be +
    type 3: 3(+) & 1(-)  OR  4(-) & 1(+)   ----> the product of the LS on all the vertexes will be -
    
    Use this last result to distinguish between i_indexes_of_TYPES_3_and_4_cells and i_indexes_of_TYPES_1_and_2_cells
     
    """
    i_indexes_of_TYPES_3_and_4_cells_IN_i_indexes_of_fictitius_cells=np.where(np.prod([LS_i_times_LS_c, LS_b_times_LS_a], axis=0) < 0.)[0]
    i_indexes_of_TYPES_3_and_4_cells= i_indexes_of_fictitius_cells[i_indexes_of_TYPES_3_and_4_cells_IN_i_indexes_of_fictitius_cells]
    i_indexes_of_TYPES_1_and_2_cells = np.setdiff1d(i_indexes_of_fictitius_cells,i_indexes_of_TYPES_3_and_4_cells)
    i_indexes_of_TYPE_1_cells = np.setdiff1d(i_indexes_of_TYPES_1_and_2_cells,i_indexes_of_TYPE_2_cells)

    i_indexes_of_TYPE_3_cells_temp=np.where((np.greater(LS_i[i_indexes_of_TYPES_3_and_4_cells_IN_i_indexes_of_fictitius_cells], 0.).astype(int) +
              np.greater(LS_c[i_indexes_of_TYPES_3_and_4_cells_IN_i_indexes_of_fictitius_cells], 0.).astype(int) +
              np.greater(LS_b[i_indexes_of_TYPES_3_and_4_cells_IN_i_indexes_of_fictitius_cells], 0.).astype(int)) > 1)[
        0]
    i_indexes_of_TYPE_3_cells = i_indexes_of_TYPES_3_and_4_cells[i_indexes_of_TYPE_3_cells_temp]
    i_indexes_of_TYPE_4_cells = np.delete(i_indexes_of_TYPES_3_and_4_cells,i_indexes_of_TYPE_3_cells_temp)

    i_1_2_3_4_FC_names=np.concatenate((anularegion[i_indexes_of_TYPE_1_cells], anularegion[i_indexes_of_TYPE_2_cells],
                    anularegion[i_indexes_of_TYPE_3_cells], anularegion[i_indexes_of_TYPE_4_cells]))

    # the following is a test that can be removed for speed
    # try:
    #     if np.setdiff1d(anularegion[i_indexes_of_fictitius_cells],np.concatenate((anularegion[i_indexes_of_TYPE_1_cells], anularegion[i_indexes_of_TYPE_2_cells], anularegion[i_indexes_of_TYPE_3_cells], anularegion[i_indexes_of_TYPE_4_cells]))).size > 0:
    #         raise FileNotFoundError
    # except FileNotFoundError:
    #     print("ERROR: this function has an error")

    # make dictionaries:
    i_1_2_3_4_FC_type = dict(zip(anularegion[i_indexes_of_TYPE_1_cells].astype(str).tolist(), np.ones(i_indexes_of_TYPE_1_cells.size).astype(int).tolist()))
    i_1_2_3_4_FC_type.update(dict(zip(anularegion[i_indexes_of_TYPE_2_cells].astype(str).tolist(), np.full(i_indexes_of_TYPE_2_cells.size, 2,dtype=int).tolist())))
    i_1_2_3_4_FC_type.update(dict(zip(anularegion[i_indexes_of_TYPE_3_cells].astype(str).tolist(), np.full(i_indexes_of_TYPE_3_cells.size, 3,dtype=int).tolist())))
    i_1_2_3_4_FC_type.update(dict(zip(anularegion[i_indexes_of_TYPE_4_cells].astype(str).tolist(), np.full(i_indexes_of_TYPE_4_cells.size, 4,dtype=int).tolist())))

    dict_FC_names = dict(zip(i_1_2_3_4_FC_names.astype(str).tolist(),i_1_2_3_4_FC_names.astype(int).tolist()))

    return i_1_2_3_4_FC_names, i_indexes_of_TYPE_2_cells.size, i_1_2_3_4_FC_type, dict_FC_names

def split_central_from_noncentral_intersections(indexesFC_TYPE_,Fracturelist,mesh,sgndDist_k):
    # if the sum of LS=0 then the front is passing in the middle of the cell
    LS_TYPE_ = get_LS_on_i_fictitius_cell("icba",Fracturelist[indexesFC_TYPE_], mesh.NeiElements, sgndDist_k)
    # todo: one could think to speed up the code by setting the condition below to >=0 but I am not sure it should be
    # for alle the cells
    central_intersections = np.where(np.sum(LS_TYPE_, axis=1) == 0)[0]

    if central_intersections.size > 0:
        other_intersections = np.setdiff1d(range(indexesFC_TYPE_.size), central_intersections)
        return indexesFC_TYPE_[central_intersections], indexesFC_TYPE_[other_intersections]
    else:
        return [], indexesFC_TYPE_

def define_orientation_type1(T1_other_intersections, mesh, sgndDist_k):
    """
            type 1        |                 |                 |
            2(+) & 2(-)   |                 |                 |
                 2        |        3        |        1        |        0
            - ------ -    |   - ------ +    |    + ------ -   |    + ------ +
            |        |    |   |        |    |    |        |   |    |        |
            |        |    |   |        |    |    |        |   |    |        |
            + ------ +    |   - ------ +    |    + ------ -   |    - ------ -
    """
    LS_TYPE_1 = get_LS_on_i_fictitius_cell("ab",T1_other_intersections, mesh.NeiElements, sgndDist_k)
    testvector = np.asarray([[2],
                             [1]], dtype=int)
    orientation = np.transpose(np.matmul(LS_TYPE_1 > 0., testvector))
    """
    now the orientation is like this:
            type 1        |                 |                 |
            2(+) & 2(-)   |                 |                 |
                 0        |        1        |        2        |        3
            - ------ -    |   - ------ +    |    + ------ -   |    + ------ +
            |        |    |   |        |    |    |        |   |    |        |
            |        |    |   |        |    |    |        |   |    |        |
            + ------ +    |   - ------ +    |    + ------ -   |    - ------ -
            
    We want to make it as above by applying a function
    f : a + bx + cx^2 + dx^3
    f(0)->2, f(1)->3, f(2)->1, f(3)->0
     a=2, b=23/6, c=-7/2, d=2/3
    """
    f = lambda x: 2+23*x/6-7*x*x/2+2*x*x*x/3
    vf=np.vectorize(f)
    return vf(orientation).astype(int)

def define_orientation_type2(T2_other_intersections, mesh, sgndDist_k):
    # todo: check the boolean
    """
            type 2        |
            2(+) & 2(-)   |
                 0        |        1
            + ------ -    |   - ------ +
            |        |    |   |        |
            |        |    |   |        |
            - ------ +    |   + ------ -
    """
    LS_TYPE_2 = get_LS_on_i_fictitius_cell("i",T2_other_intersections, mesh.NeiElements, sgndDist_k)
    return np.transpose(LS_TYPE_2 > 0.)

def define_orientation_type3OR4(type,Tx_other_intersections, mesh, sgndDist_k):
    """
                        type 3        |                 |                 |                 |
                        3(+) & 1(-)   |                 |                 |                 |
    RETURNED                 1        |        2        |        3        |        0        |
    ORIENTATION:        + ------ +    |   + ------ -    |    - ------ +   |    + ------ +   |    a ------ b
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |
                        + ------ -    |   + ------ +    |    + ------ +   |    - ------ +   |    i ------ c

                        type 4        |                 |                 |                 |
    RETURNED            3(-) & 1(+)   |                 |                 |                 |
    ORIENTATION:             1        |        2        |        3        |        0        |
                        - ------ -    |   - ------ +    |    + ------ -   |    - ------ -   |    a ------ b
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |
                        - ------ +    |   - ------ -    |    - ------ -   |    + ------ -   |    i ------ c
    """
    LS_TYPE_3or4 = get_LS_on_i_fictitius_cell("icba",Tx_other_intersections, mesh.NeiElements, sgndDist_k)
    testvector = np.asarray([1,2,3,4], dtype=int)
    if type == "3":
        LS_TYPE_3or4 = (LS_TYPE_3or4 < 0.).astype(int) # True (1) when is Negative otherwise False (0)
    elif type == "4":
        LS_TYPE_3or4 = (LS_TYPE_3or4 > 0.).astype(int) # True (1) when is Positive otherwise False (0)
    for i in range(LS_TYPE_3or4.shape[0]):
        LS_TYPE_3or4[i,:]=np.multiply(LS_TYPE_3or4[i,:], testvector)

    if (np.sum(LS_TYPE_3or4, axis=1)-1)[0] == 6 :
     print("stop")
    return (np.sum(LS_TYPE_3or4, axis=1)-1)

def move_intersections_to_the_center_when_inRibbon_type3(indexesFC_T3_central_inters,
                                                            indexesFC_T3_other_inters,
                                                            Fracturelist,
                                                            mesh,
                                                            sgndDist_k,
                                                            Ribbon):

    # define the orientation of all the cells in indexesFC_T3_other_inters
    T3_orientations = define_orientation_type3OR4("3",Fracturelist[indexesFC_T3_other_inters], mesh, sgndDist_k)

    # get the names of the negative cells in the FC in indexesFC_T3_other_inters
    T3_other_intersections_name_of_negatives = get_fictitius_cell_names(T3_orientations, Fracturelist[indexesFC_T3_other_inters], mesh.NeiElements)

    # check if the negative cells are Ribbon cells
    T3_other_intersections_test_if_Ribbon = np.isin(T3_other_intersections_name_of_negatives, Ribbon).astype(int)

    # take to the next check only the cells that are within ribbon
    indexes_temp=np.nonzero(T3_other_intersections_test_if_Ribbon)[1]
    indexesFC_T3_2_intersections=indexesFC_T3_other_inters[indexes_temp]
    indexesFC_T3_0_1_2_intersections=np.delete(indexesFC_T3_other_inters,indexes_temp)

    # compute the level set at the point at the center of the fictitius cell
    # you can compute it by simply taking the average of the LS value that is known at the vertexes of
    # the fictitius cell
    if indexesFC_T3_2_intersections.size > 0:
        LS_TYPE_3 = get_LS_on_i_fictitius_cell("iabc", Fracturelist[indexesFC_T3_2_intersections], mesh.NeiElements, sgndDist_k)

        # if the level set value at that point is > 0 then the front is intersecting the
        # ribbon cell, so what you have to do is move the name of the cells where to take the centre as
        # intersecting point
        to_move_to_the_center=np.where(np.sum(LS_TYPE_3, axis=1)/4. > 0.)[0]
        if to_move_to_the_center.size > 0:
            indexesFC_T3_central_inters = np.concatenate((indexesFC_T3_central_inters,indexesFC_T3_2_intersections[to_move_to_the_center])).astype(int)
            indexesFC_T3_2_intersections = np.delete(indexesFC_T3_2_intersections,to_move_to_the_center)
    return indexesFC_T3_central_inters, indexesFC_T3_2_intersections, indexesFC_T3_0_1_2_intersections

def move_intersections_to_the_center_when_inRibbon_type1(
    T1_central_intersections, T1_other_intersections, Fracturelist,mesh, sgndDist_k, Ribbon):

    # define the orientation of all the cells in T1_other_intersections
    T1_1st_negative_cell_local_index = define_orientation_type1(Fracturelist[T1_other_intersections], mesh, sgndDist_k)
    T1_2nd_negative_cell_local_index = np.mod(T1_1st_negative_cell_local_index+1,4)

    # get the names of the negative cells
    T1_1st_negative_cell_name = get_fictitius_cell_names(np.transpose(T1_1st_negative_cell_local_index), Fracturelist[T1_other_intersections], mesh.NeiElements)
    T1_2nd_negative_cell_name = get_fictitius_cell_names(np.transpose(T1_2nd_negative_cell_local_index), Fracturelist[T1_other_intersections], mesh.NeiElements)


    # check if the negative cells are Ribbon cells
    T1_1st_negative_cell_checkif_Ribbon = np.isin(T1_1st_negative_cell_name, Ribbon).astype(int)
    T1_2nd_negative_cell_checkif_Ribbon = np.isin(T1_2nd_negative_cell_name, Ribbon).astype(int)


    # return True if any of them is in ribbon
    T1_negative_cell_checkif_Ribbon = T1_1st_negative_cell_checkif_Ribbon+T1_2nd_negative_cell_checkif_Ribbon


    # take to the next check only the cells that are within ribbon
    indexes_temp=np.nonzero(T1_negative_cell_checkif_Ribbon)[1]
    T1_close_to_ribbon=T1_other_intersections[indexes_temp]
    T1_far_from_ribbon=np.delete(T1_other_intersections,indexes_temp)

    # compute the level set at the point at the center of the fictitius cell
    # you can compute it by simply taking the average of the LS value that is known at the vertexes of
    # the fictitius cell
    if T1_close_to_ribbon.size > 0:
        LS_TYPE_1 = get_LS_on_i_fictitius_cell("iabc", Fracturelist[T1_close_to_ribbon], mesh.NeiElements, sgndDist_k)

        # if the level set value at that point is > 0 then the front is intersecting the
        # ribbon cell, so what you have to do is move the name of the cells where to take the centre as
        # intersecting point
        to_move_to_the_center=np.where(np.sum(LS_TYPE_1, axis=1)/4. > 0.)[0]
        if to_move_to_the_center.size > 0:
            T1_central_intersections = np.concatenate((T1_central_intersections,T1_close_to_ribbon[to_move_to_the_center])).astype(int)
            T1_close_to_ribbon = np.delete(T1_close_to_ribbon,to_move_to_the_center)
    return T1_central_intersections, np.concatenate((T1_close_to_ribbon, T1_far_from_ribbon))

def get_mesh_info_for_computing_intersections(i,mesh,sgndDist_k):

    # get the level set at the vertex of all these fictitius cells
    LS_other_intersections = get_LS_on_i_fictitius_cell("icba", i, mesh.NeiElements, sgndDist_k)

    # get the name of the node at the center of the fictitius cell: 1
    #
    #    o---------o---------o
    #    |         |         |
    #    |    a ------- b    |
    #    |    |    |    |    |
    #    o----|----1----|----o
    #    |    |    |    |    |
    #    |    i ------- c    |
    #    |         |         |
    #    o---------o---------o
    centernode = mesh.Connectivity[i, 2]

    # get the coordinates of the vertical and horizontal line passing for the center node
    xgrid = mesh.VertexCoor[centernode, 0]
    ygrid = mesh.VertexCoor[centernode, 1]

    # get the names of the elements c b a
    # c = right
    # b = rightup
    # a = up
    #
    #    o---------o---------o
    #    |         |         |
    #    |    a ------- b    |
    #    |    |    |    |    |
    #    o----|----o----|----o
    #    |    |    |    |    |
    #    |    i ------- c    |
    #    |         |         |
    #    o---------o---------o

    #    0     1      2      3
    # NeiElements[i]->[left, right, bottom, up]
    [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]
    #
    up = mesh.NeiElements[i, top_elem]
    right = mesh.NeiElements[i, right_elem]
    rightUp = mesh.NeiElements[i + 1, top_elem]

    # get the coordinates of the centers of the cells iabc
    allx = np.asarray(
        [mesh.CenterCoor[right, 0], mesh.CenterCoor[i, 0], mesh.CenterCoor[up, 0], mesh.CenterCoor[rightUp, 0]])
    ally = np.asarray(
        [mesh.CenterCoor[up, 1], mesh.CenterCoor[rightUp, 1], mesh.CenterCoor[right, 1], mesh.CenterCoor[i, 1]])

    return xgrid, ygrid, allx, ally, LS_other_intersections

def find_x_OR_y_intersections(intersection_with,XorYgrid,numberofinters,allx,ally,float_precision,LS):

    # get the coefficients for
    alphaXorY = np.empty((4, numberofinters), dtype=float_precision)

    # compute the alphaX and alphaY vectors that will be used to compute the intersections
    if intersection_with == "x":  # intersection between the front and the Horizontal line
        allXorY = allx
        alphaXorY[[0, 2], :] = (XorYgrid - ally[[0, 2], :])
        alphaXorY[[1, 3], :] = -(XorYgrid - ally[[1, 3], :])

    elif intersection_with == "y":     # intersection between the front and the Vertical line
        allXorY = ally
        alphaXorY[[0, 2], :] = (XorYgrid - allx[[0, 2], :])
        alphaXorY[[1, 3], :] = -(XorYgrid - allx[[1, 3], :])

    # compute some products fo the computations of the intersections
    doubledotProdwithAlphaXorY = np.multiply(np.transpose(alphaXorY), LS)
    innerProdwithAlphaXorY = np.sum(doubledotProdwithAlphaXorY, axis=1)

    # intersection between the front and the Vertical or Horizontal line
    YorX = np.divide(np.einsum('ij,ji->i', doubledotProdwithAlphaXorY, allXorY), innerProdwithAlphaXorY)

    return YorX

def find_edge_ID(xCandidate,xgrid,yCandidate,ygrid,mesh,i):

    # define if the xintersection is between the right cells or on the left ones
    x_position = ((xCandidate - xgrid) > 0).astype(int)

    # define the edge ID [ leftIDs, rightIDs ]
    #                         0       1
    IDs0, IDs1 = get_fictitius_cell_specific_names("left right", i, mesh.NeiElements)
    row_idx = np.arange(0, x_position.shape[0], 1, dtype=int)
    # very nice peace of code below: I am randoimly specific positions from the matrix
    IDs0 = IDs0[[row_idx[None, :], x_position]].transpose()
    IDs1 = IDs1[[row_idx[None, :], x_position]].transpose()
    edge_x = []
    for j in range(IDs0.size):
        edge_x.append(np.intersect1d(mesh.Connectivityelemedges[IDs0[j]], mesh.Connectivityelemedges[IDs1[j]],
                                   assume_unique=True)[0])

    # define if the yintersection is between the top cells or between the bottom ones
    y_position = ((yCandidate - ygrid) > 0).astype(int)
    # define the edge ID [ bottomID, topID ]
    #                         0       1
    IDs0, IDs1 = get_fictitius_cell_specific_names("bottom top", i, mesh.NeiElements)
    row_idx = np.arange(0, y_position.shape[0], 1, dtype=int)
    # very nice peace of code below: I am randoimly specific positions from the matrix
    IDs0 = IDs0[[row_idx[None, :], y_position]].transpose()
    IDs1 = IDs1[[row_idx[None, :], y_position]].transpose()
    edge_y = []
    for j in range(IDs0.size):
        edge_y.append(np.intersect1d(mesh.Connectivityelemedges[IDs0[j]], mesh.Connectivityelemedges[IDs1[j]],
                                   assume_unique=True)[0])
    return edge_x, edge_y

def find_xy_intersections_type3_case_2_intersections(return_info, indexesFC_T3_2_intersections,
                                                      Fracturelist, mesh, sgndDist_k,float_precision):
    i=Fracturelist[indexesFC_T3_2_intersections]
    #
    xgrid, ygrid, allx, ally, LS_other_intersections = get_mesh_info_for_computing_intersections(i, mesh, sgndDist_k)

    # intersection between the front and the Horizontal line
    xCandidate = find_x_OR_y_intersections("x", ygrid, i.size, allx, ally, float_precision, LS_other_intersections)
    # and ygrid

    # intersection between the front and the Vertical line
    yCandidate = find_x_OR_y_intersections("y", xgrid, i.size, allx, ally, float_precision, LS_other_intersections)
    # and xgrid

    if xCandidate.size > 0:
        edge_x,edge_y = find_edge_ID(xCandidate, xgrid, yCandidate, ygrid, mesh, i)

    if return_info == "return xy":
        edgeORvertexID = []
        if xCandidate.size > 0:
            x, y, edge_2_inter = reorder_intersections(Fracturelist,
                                                       xCandidate,
                                                       yCandidate,
                                                       xgrid,
                                                       ygrid,
                                                       edge_x,
                                                       edge_y,
                                                       mesh,
                                                       indexesFC_T3_2_intersections)
            edgeORvertexID.extend(edge_2_inter)
        else :
            x = y = []
        return x,y,edgeORvertexID

    elif return_info == "return all xy":
        return xCandidate,xgrid,ygrid,yCandidate,np.asarray(edge_x),np.asarray(edge_y)

def check_if_point_inside_cell(xORy_grid,xORy_Candidate,hx_OR_hy,mac_precision):
    xORy_max = xORy_grid + hx_OR_hy * .5
    xORy_min = xORy_grid - hx_OR_hy * .5
    a=np.max(np.column_stack((np.abs(xORy_Candidate), np.abs(xORy_max), np.ones(xORy_max.size))), axis=1)
    b=np.max(np.column_stack((np.abs(xORy_Candidate), np.abs(xORy_min), np.ones(xORy_min.size))), axis=1)
    return ((xORy_Candidate - xORy_max) / a <= mac_precision ) * ((xORy_Candidate - xORy_min) / b >= -mac_precision )

def reorder_intersections(Fracturelist,
                          xCandidate_2_inter,
                          yCandidate_2_inter,
                          xgrid_2_inter ,
                          ygrid_2_inter,
                          edge_x_2_inter,
                          edge_y_2_inter,
                          mesh,
                          indexesFC_Tx_2_intersections_local):
    """
    We need to order the points: does it comes irst x-intersection or y-intersection?
    We need to understand the location of the points in the fictitius cell (A1, A2, B1, B2) and WHERE the front
    is coming (L R T B) i.e. the previous fictitius cell.

            |     ____|____     |
                 |T        |
     _ _ _ _|_ _ |_ _ |_ _ |_ _ | _ _ _ _ _ _
                 |         |
         ___|____|____|____|____|___
        |        |    B2   |        |
     _ _| _ | _ _|_A1_|_A2_| _ _|_ _|_ _ _
        |L       |    B1   |       R|
        |___|____|____|____|____|___|
                 |         |
    _ _ _ _ | _ _|_ _ |_ _ |_ _ | _ _ _ _
                 |B        |
            |    |____|____|    |

            |         |         |

    The following table is providing us a way of deciding if we need to get fist the intersection with the horizontal
    axis or the vertical one. If we consider the former case then we have 0 otherwise 1.

          (A1-B1)  (A2-B2)  (A2-B1)  (A1-B2)            (A1-B1)  (A2-B2)  (A2-B1)  (A1-B2)             0 1 2 3        This vector form is more easy to access
      L     A1       B2       B1       A1             L    x        y        y        x             0  0 1 1 0        i values 0       - 1       - 2         - 3
      R     B1       A2       A2       B2      <=>    R    y        x        x        y       <=>   1  1 0 0 1   <=>  j values 0 1 2 3 - 0 1 2 3 - 0 1 2  3  - 0  1  2  3
      B     B1       A2       B1       A1             B    y        x        y        x             2  1 0 1 0        indexes  0 1 2 3   4 5 6 7   8 9 10 11 - 12 13 14 15
      T     A1       B2       A2       B2             T    x        y        x        y             3  0 1 0 1                 0 1 1 0 - 1 0 0 1 - 1 0  1  0 -  0  1  0  1
    """

    # take the names of the fictitius cells
    i = Fracturelist[indexesFC_Tx_2_intersections_local]
    # take all 4 neighbours elements
    #                         0     1      2      3
    #       NeiElements[i]->[left, right, bottom, up]
    matrix_with_rows_where_to_search = mesh.NeiElements[i]
    # thake the index of the previous fictitius cell (where the front is coming)
    array_with_the_number_to_be_searched_in_each_row = Fracturelist[indexesFC_Tx_2_intersections_local - 1]
    # OLD matrix of indexes:
    # m=np.asarray([[0,1,1,0],
    #               [1,0,0,1],
    #               [0,1,0,1],
    #               [1,0,1,0]],dtype=int)
    # I have written the matrix as an array beaqcuse is easier to access
    m = np.asarray([0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1], dtype=int)

    # array of 1D coordinates
    ij = np.full((indexesFC_Tx_2_intersections_local.size), 3, dtype=int)

    # find the i values
    # todo: may be a more efficient way exist
    for jj in range(0, indexesFC_Tx_2_intersections_local.size):
        ij[jj] = \
        np.where(matrix_with_rows_where_to_search[jj, :] == array_with_the_number_to_be_searched_in_each_row[jj])[0][0]
    # multiply each i value by 4 to compute the index for the array
    ij = ij * 4
    """
    the following lines are providing the values on the table below depending on the test conditions: 

      x>xgrid ?
    False   True
      0       2  False 
                       y>ygrid ?
      3       1  True

    the values will fill the second column of the matrix ij
    """
    a = 2 * ((xCandidate_2_inter - xgrid_2_inter > 0).astype(int))
    b = (yCandidate_2_inter - ygrid_2_inter > 0).astype(int)
    ij = ij + np.multiply(a, -2 * b + 1) + 3 * b

    # now we need to get the values from the matrix m by knowing the indexes
    # that have been stored in the matrix ij
    m = m[ij]
    # if m[i] is zero take as first the intersection with x axes, otherwise with y axes
    # todo: may be a more efficient way exist
    edge_2_inter = []
    xtemp = []
    ytemp = []
    for jj in range(m.size):
        if m[jj] == 0:
            xtemp.append([xCandidate_2_inter[jj],xgrid_2_inter[jj]])
            ytemp.append([ygrid_2_inter[jj],yCandidate_2_inter[jj]])

            edge_2_inter.append([edge_x_2_inter[jj],edge_y_2_inter[jj]])
        else:
            xtemp.append([xgrid_2_inter[jj],xCandidate_2_inter[jj]])
            ytemp.append([yCandidate_2_inter[jj],ygrid_2_inter[jj]])

            edge_2_inter.append([edge_y_2_inter[jj],edge_x_2_inter[jj]])

    return  xtemp, ytemp, edge_2_inter

def find_xy_intersections_type3_case_0_1_2_intersections(    indexesFC_T3_0_1_2_intersections,
        Fracturelist, mesh, sgndDist_k,float_precision,mac_precision):
    # one assumption behind this function is that the front is curved within cells type 3
    # so there will be always an intersection with both axes whereas within cells type 1 you can have straight front
    # and thus more checks are needed

    xCandidate,xgrid,ygrid,yCandidate,edge_x,edge_y = find_xy_intersections_type3_case_2_intersections("return all xy",
                                                                                indexesFC_T3_0_1_2_intersections,
                                                                                Fracturelist,
                                                                                mesh,
                                                                                sgndDist_k,
                                                                                float_precision)
    # we can have 0, 1, 2 intersections.
    # In the latter case they need to be ordered properly.
    # Now we will count the intersections per FC
    is_X_inside_the_cell_Answer = check_if_point_inside_cell(xgrid,xCandidate,mesh.hx,mac_precision).astype(int)
    is_Y_inside_the_cell_Answer = check_if_point_inside_cell(ygrid,yCandidate,mesh.hy,mac_precision).astype(int)
    number_of_intersections =  is_X_inside_the_cell_Answer + is_Y_inside_the_cell_Answer

    # find where I have two intersections
    temp_indexes = np.where(number_of_intersections == 2)[0]

    # separate the case with two intersection from the case with 0 or 1
    indexesFC_T3_2_intersections_local = indexesFC_T3_0_1_2_intersections[temp_indexes]
    xCandidate_2_inter =  xCandidate[temp_indexes]
    ygrid_2_inter =       ygrid     [temp_indexes]
    yCandidate_2_inter =  yCandidate[temp_indexes]
    xgrid_2_inter =       xgrid     [temp_indexes]
    edge_x_2_inter =      edge_x    [temp_indexes]
    edge_y_2_inter =      edge_y    [temp_indexes]

    indexesFC_T3_0_1_intersection_local = np.delete(indexesFC_T3_0_1_2_intersections,temp_indexes)
    xCandidate = np.delete(xCandidate,temp_indexes)
    ygrid =      np.delete(ygrid,     temp_indexes)
    yCandidate = np.delete(yCandidate,temp_indexes)
    xgrid =      np.delete(xgrid,     temp_indexes)
    edge_x = np.delete(edge_x ,temp_indexes)
    edge_y = np.delete(edge_y, temp_indexes)
    is_X_inside_the_cell_Answer = np.delete(is_X_inside_the_cell_Answer, temp_indexes)
    is_Y_inside_the_cell_Answer = np.delete(is_Y_inside_the_cell_Answer, temp_indexes)
    number_of_intersections = np.delete(number_of_intersections, temp_indexes)

    # find where I have no intersections
    temp_indexes = np.where(number_of_intersections == 0)[0]

    # separate the case with 0 intersection from the case with 1
    indexesFC_T3_0_intersection_local = indexesFC_T3_0_1_intersection_local[temp_indexes]
    indexesFC_T3_1_intersection_local = np.delete(indexesFC_T3_0_1_intersection_local,temp_indexes)
    xCandidate = np.delete(xCandidate,temp_indexes)
    ygrid =      np.delete(ygrid,     temp_indexes)
    yCandidate = np.delete(yCandidate,temp_indexes)
    xgrid =      np.delete(xgrid,     temp_indexes)
    edge_x = np.delete(edge_x ,temp_indexes)
    edge_y = np.delete(edge_y, temp_indexes)
    is_X_inside_the_cell_Answer = np.delete(is_X_inside_the_cell_Answer, temp_indexes)
    is_Y_inside_the_cell_Answer = np.delete(is_Y_inside_the_cell_Answer, temp_indexes)

    # check if the steps before have been done correctly
    if is_X_inside_the_cell_Answer.size > 0:
        if is_X_inside_the_cell_Answer.max() > 1:
            raise SystemExit('ERROR: the processing of the cells is not correct')


    # processing the case of single intersection
    # setting xCandidate and xgrid within an unique array: xCandidate
    edge_1_inters = edge_x
    temp_indexes = np.nonzero(is_Y_inside_the_cell_Answer.astype(int))
    edge_1_inters[temp_indexes] = edge_y[temp_indexes]
    temp_indexes = np.nonzero(is_Y_inside_the_cell_Answer.astype(int))[0]
    xCandidate[temp_indexes]=xgrid[temp_indexes]
    temp_indexes = np.nonzero(is_X_inside_the_cell_Answer.astype(int))[0]
    yCandidate[temp_indexes]=ygrid[temp_indexes]

    # we need to order the points
    if indexesFC_T3_2_intersections_local.size > 0 :
        xCandidate_2_inter, yCandidate_2_inter, edge_2_inter = reorder_intersections(Fracturelist,
                                                                                     xCandidate_2_inter,
                                                                                     yCandidate_2_inter,
                                                                                     xgrid_2_inter ,
                                                                                     ygrid_2_inter,
                                                                                     edge_x_2_inter,
                                                                                     edge_y_2_inter,
                                                                                     mesh,
                                                                                     indexesFC_T3_2_intersections_local)
    else: edge_2_inter=[]

    return indexesFC_T3_0_intersection_local, \
           indexesFC_T3_1_intersection_local, \
           indexesFC_T3_2_intersections_local, \
           xCandidate,yCandidate,edge_1_inters,\
           xCandidate_2_inter,yCandidate_2_inter,edge_2_inter

def find_xy_intersections_type1( indexesFC_T1_1_2_intersections,
                                 Fracturelist,mesh, sgndDist_k, float_precision,mac_precision):

    # 1 or 2 intersections per fictitius cell are allowed

    # we expect to have some NaN or some points outside of the cells
    [xCandidate,
     xgrid,
     ygrid,
     yCandidate,
     edge_x,edge_y] = find_xy_intersections_type3_case_2_intersections("return all xy",
                                                                        indexesFC_T1_1_2_intersections,
                                                                        Fracturelist,
                                                                        mesh,
                                                                        sgndDist_k,
                                                                        float_precision)


    # check the exstistance of nan
    # if any of xCandidate or any of yCandidate is nan, substitute it with the coordinate of a point out of the mesh
    if any(xCandidate) or any(yCandidate) is np.nan:
        nan_values = np.where(xCandidate == np.nan)
        xCandidate[nan_values] = mesh.CenterCoor[0][0]-mesh.hx
        nan_values = np.where(yCandidate == np.nan)
        xCandidate[nan_values] = mesh.CenterCoor[0][1]-mesh.hy


    # we can have 1, 2 intersections.
    # In the latter case they need to be ordered properly.
    # Now we will count the intersections per FC
    is_X_inside_the_cell_Answer = check_if_point_inside_cell(xgrid,xCandidate,mesh.hx,mac_precision).astype(int)
    is_Y_inside_the_cell_Answer = check_if_point_inside_cell(ygrid,yCandidate,mesh.hy,mac_precision).astype(int)
    number_of_intersections = is_X_inside_the_cell_Answer + is_Y_inside_the_cell_Answer

    # find where I have two intersections
    temp_indexes = np.where(number_of_intersections == 2)[0]

    # separate the case with two intersection from the case with 1
    indexesFC_T1_2_intersections_local = indexesFC_T1_1_2_intersections[temp_indexes]
    xCandidate_2_inter =  xCandidate[temp_indexes]
    ygrid_2_inter =       ygrid     [temp_indexes]
    yCandidate_2_inter =  yCandidate[temp_indexes]
    xgrid_2_inter =       xgrid     [temp_indexes]
    edge_x_2_inter =      edge_x    [temp_indexes]
    edge_y_2_inter =      edge_y    [temp_indexes]

    indexesFC_T1_1_intersection_local = np.delete(indexesFC_T1_1_2_intersections,temp_indexes)
    xCandidate = np.delete(xCandidate,temp_indexes)
    ygrid =      np.delete(ygrid,     temp_indexes)
    yCandidate = np.delete(yCandidate,temp_indexes)
    xgrid =      np.delete(xgrid,     temp_indexes)
    edge_x =     np.delete(edge_x ,temp_indexes)
    edge_y =     np.delete(edge_y, temp_indexes)
    is_X_inside_the_cell_Answer = np.delete(is_X_inside_the_cell_Answer, temp_indexes)
    is_Y_inside_the_cell_Answer = np.delete(is_Y_inside_the_cell_Answer, temp_indexes)


    # check if the steps before have been done correctly
    if is_X_inside_the_cell_Answer.size > 0:
        if is_X_inside_the_cell_Answer.max() > 1:
            raise SystemExit('ERROR: the processing of the cells is not correct')


    # processing the case of single intersection
    # setting xCandidate and xgrid within an unique array: xCandidate
    edge_1_inters = edge_x
    temp_indexes = np.nonzero(is_Y_inside_the_cell_Answer.astype(int))[0]
    edge_1_inters[temp_indexes] = edge_y[temp_indexes]
    temp_indexes = np.nonzero(is_Y_inside_the_cell_Answer.astype(int))[0]
    xCandidate[temp_indexes]=xgrid[temp_indexes]
    temp_indexes = np.nonzero(is_X_inside_the_cell_Answer.astype(int))[0]
    yCandidate[temp_indexes]=ygrid[temp_indexes]

    if indexesFC_T1_2_intersections_local.size > 0 :
        xCandidate_2_inter, yCandidate_2_inter, edge_2_inter = reorder_intersections(Fracturelist,
                                                                                     xCandidate_2_inter,
                                                                                     yCandidate_2_inter,
                                                                                     xgrid_2_inter ,
                                                                                     ygrid_2_inter,
                                                                                     edge_x_2_inter,
                                                                                     edge_y_2_inter,
                                                                                     mesh,
                                                                                     indexesFC_T1_2_intersections_local)
    else: edge_2_inter=[]

    return indexesFC_T1_1_intersection_local, \
           indexesFC_T1_2_intersections_local, \
           xCandidate,yCandidate,edge_1_inters,\
           xCandidate_2_inter,yCandidate_2_inter,edge_2_inter

def find_xy_intersections_with_cell_center(indexesFC_Tx_central_inters,Fracturelist,mesh):

    # define a more practical name
    i = Fracturelist[indexesFC_Tx_central_inters]

    # take the coordinates
    centernode = mesh.Connectivity[i, 2]
    x=mesh.VertexCoor[centernode, 0]
    y=mesh.VertexCoor[centernode, 1]

    edgeORvertexID = []

    # append infos
    if centernode.size > 0:
        edgeORvertexID.extend(centernode)  # intersecting with a vertex
    return x,y,edgeORvertexID

def process_fictitius_cells_3(indexesFC_TYPE_3,Args, x, y, typeindex,edgeORvertexID):

    [Fracturelist, Ribbon, mesh, sgndDist_k, float_precision, mac_precision] = Args

    # find when you have an intersection with the cell center or when you have two intersections
    [indexesFC_T3_central_inters, indexesFC_T3_other_inters] = split_central_from_noncentral_intersections(np.asarray(indexesFC_TYPE_3),Fracturelist,mesh,sgndDist_k)

    # if the intersection will be in the ribbon cell, move these cells
    # from the other intersections to the central intersection list
    [indexesFC_T3_central_inters,
     indexesFC_T3_2_intersections,
     indexesFC_T3_0_1_2_intersections] = move_intersections_to_the_center_when_inRibbon_type3(indexesFC_T3_central_inters,
                                                                                    indexesFC_T3_other_inters,
                                                                                    Fracturelist,
                                                                                    mesh,
                                                                                    sgndDist_k,
                                                                                    Ribbon)


    # find the intersections with the center
    # 1 intersection
    [T3_x_inters_center,
     T3_y_inters_center,
     T3_edgeORvertexID_center] = find_xy_intersections_with_cell_center(indexesFC_T3_central_inters,
                                                                        Fracturelist,
                                                                        mesh)

    # set the found intersections
    for j in range(len(indexesFC_T3_central_inters)):
        temp_index = indexesFC_T3_central_inters[j]
        x[temp_index ] = [T3_x_inters_center[j]]
        y[temp_index ] = [T3_y_inters_center[j]]
        edgeORvertexID[temp_index ] = [T3_edgeORvertexID_center[j]]
        typeindex[temp_index ] = [1]


    # find the intersections with the vertical and horizontal axes passing throug the cell center
    # 2 intersections
    [T3_x_inters,
     T3_y_inters,
     T3_edgeORvertexID] = find_xy_intersections_type3_case_2_intersections("return xy",
                                                                           indexesFC_T3_2_intersections,
                                                                           Fracturelist,
                                                                           mesh,
                                                                           sgndDist_k,
                                                                           float_precision)
    # set the found intersections
    for j in range(indexesFC_T3_2_intersections.size):
        temp_index = indexesFC_T3_2_intersections[j]
        x[temp_index ] = T3_x_inters[j]
        y[temp_index ] = T3_y_inters[j]
        edgeORvertexID[temp_index] = T3_edgeORvertexID[j]
        typeindex[temp_index ] = [0,0]

    # 0,1,2 intersections
    [indexesFC_T3_0_intersection_local,
     indexesFC_T3_1_intersection_local,
     indexesFC_T3_2_intersections_local,
     xCandidate,yCandidate,edge_1_inters,
     xCandidate_2_inter,yCandidate_2_inter,edge_2_inter] = find_xy_intersections_type3_case_0_1_2_intersections(indexesFC_T3_0_1_2_intersections,
                                                                                                                Fracturelist,
                                                                                                                mesh,sgndDist_k,float_precision,mac_precision)
    # set the found intersections
    for j in range(indexesFC_T3_0_intersection_local.size):
        temp_index = indexesFC_T3_0_intersection_local[j]
        x[temp_index ] = []
        y[temp_index ] = []
        edgeORvertexID[temp_index ] = []
        typeindex[temp_index ] = []

    for j in range(indexesFC_T3_1_intersection_local.size):
        temp_index = indexesFC_T3_1_intersection_local[j]
        x[temp_index ] = [xCandidate[j]]
        y[temp_index ] = [yCandidate[j]]
        edgeORvertexID[temp_index ] = [edge_1_inters[j]]
        typeindex[temp_index ] = [0]

    for j in range(indexesFC_T3_2_intersections_local.size):
        temp_index = indexesFC_T3_2_intersections_local[j]
        x[temp_index ] = xCandidate_2_inter[j]
        y[temp_index ] = yCandidate_2_inter[j]
        edgeORvertexID[temp_index ] = edge_2_inter[j]
        typeindex[temp_index ] = [0,0]

    return [ x, y, typeindex, edgeORvertexID]

def process_fictitius_cells_1(indexesFC_TYPE_1, Args, x, y, typeindex, edgeORvertexID):

    [Fracturelist, Ribbon, mesh, sgndDist_k, float_precision, mac_precision] = Args

    # find when you have an intersection with the cell center or when you have two intersections
    [indexesFC_T1_central_inters, indexesFC_T1_other_inters] = split_central_from_noncentral_intersections(np.asarray(indexesFC_TYPE_1),Fracturelist,mesh,sgndDist_k)

    # if the intersection will be in the ribbon cell, move these cells
    # from the other intersections to the central intersection list
    [indexesFC_T1_central_inters,
     indexesFC_T1_1_2_intersections] = move_intersections_to_the_center_when_inRibbon_type1(indexesFC_T1_central_inters,
                                                                                  indexesFC_T1_other_inters,
                                                                                  Fracturelist,
                                                                                  mesh,
                                                                                  sgndDist_k,
                                                                                  Ribbon)



    # find the intersections with the center
    # 1 intersection
    [T1_x_inters_center,
     T1_y_inters_center,
     T1_edgeORvertexID_center] = find_xy_intersections_with_cell_center(indexesFC_T1_central_inters,
                                                                        Fracturelist,
                                                                        mesh)

    # set the found intersections
    for j in range(len(indexesFC_T1_central_inters)):
        temp_index = indexesFC_T1_central_inters[j]
        x[temp_index] = [T1_x_inters_center[j]]
        y[temp_index] = [T1_y_inters_center[j]]
        edgeORvertexID[temp_index] = [T1_edgeORvertexID_center[j]]
        typeindex[temp_index] = [1]


    # find the intersections with the vertical and horizontal axes passing throug the cell center
    [indexesFC_T1_1_intersection_local, \
     indexesFC_T1_2_intersections_local, \
     xCandidate,yCandidate,edge_1_inters,\
     xCandidate_2_inter,yCandidate_2_inter,edge_2_inter] = find_xy_intersections_type1(indexesFC_T1_1_2_intersections,
                                                         Fracturelist,
                                                         mesh,
                                                         sgndDist_k,
                                                         float_precision,
                                                         mac_precision)
    for j in range(indexesFC_T1_1_intersection_local.size):
        temp_index = indexesFC_T1_1_intersection_local[j]
        x[temp_index] = [xCandidate[j]]
        y[temp_index] = [yCandidate[j]]
        edgeORvertexID[temp_index]  = [edge_1_inters[j]]
        typeindex[temp_index] = [0]

    for j in range(indexesFC_T1_2_intersections_local.size):
        temp_index = indexesFC_T1_2_intersections_local[j]
        x[temp_index] = xCandidate_2_inter[j]
        y[temp_index] = yCandidate_2_inter[j]
        edgeORvertexID[temp_index] = edge_2_inter[j]
        typeindex[temp_index] = [0,0]


    return [x, y, typeindex, edgeORvertexID]

def split_type4SubType4_from_rest(indexesFC_TYPE_4,Fracturelist,mesh,sgndDist_k,Ribbon):
    # check in each FC if any of the negative cells are in ribbon
    # if none of them are in Ribbon then add the index of the FC to indexesFC_TYPE_4_ST4
    #todo: it may be done more efficiently
    indexesFC_TYPE_4_ST4 = []
    jj_list = []
    orientation4=define_orientation_type3OR4("4",Fracturelist[indexesFC_TYPE_4], mesh, sgndDist_k)
    icbamesh=get_fictitius_cell_all_names(Fracturelist[indexesFC_TYPE_4], mesh.NeiElements)
    for jj in range(indexesFC_TYPE_4.size):
        negative_cells=np.delete(icbamesh[jj,:],orientation4[jj])
        if np.sum(np.isin(negative_cells,Ribbon).astype(int)) < 1:
            jj_list.append(jj)
    if len(jj_list) > 0:
        indexesFC_TYPE_4_ST4.extend(indexesFC_TYPE_4[jj_list])
        indexesFC_TYPE_4_ST01235 = np.delete(indexesFC_TYPE_4,jj_list)
        return indexesFC_TYPE_4_ST4,indexesFC_TYPE_4_ST01235
    else:
        return [], indexesFC_TYPE_4

def move_intersections_to_the_center_when_inRibbon_type4(indexesFC_T4_central_inters,
                                                         indexesFC_T4_other_inters,
                                                         Fracturelist,
                                                         mesh,
                                                         sgndDist_k):
    # NOTE: WE DO NOT NEED THE RIBBON FOR THIS...
    # compute the level set at the point at the center of the fictitius cell
    # you can compute it by simply taking the average of the LS value that is known at the vertexes of
    # the fictitius cell
    if indexesFC_T4_other_inters.size > 0:
        LS_TYPE_4 = get_LS_on_i_fictitius_cell("iabc", Fracturelist[indexesFC_T4_other_inters], mesh.NeiElements, sgndDist_k)

        # if the level set value at that point is > 0 then the front is intersecting the
        # ribbon cell, so what you have to do is move the name of the cells where to take the centre as
        # intersecting point
        to_move_to_the_center=np.where(np.sum(LS_TYPE_4, axis=1)/4. > 0.)[0]
        if to_move_to_the_center.size > 0:
            indexesFC_T4_central_inters = np.concatenate((indexesFC_T4_central_inters,indexesFC_T4_other_inters[to_move_to_the_center])).astype(int)
            indexesFC_T4_other_inters = np.delete(indexesFC_T4_other_inters,to_move_to_the_center)
    return indexesFC_T4_central_inters, indexesFC_T4_other_inters

def process_fictitius_cells_4(indexesFC_TYPE_4,Args, x, y, typeindex,edgeORvertexID):
    """
    type 4 -> 3(-) & 1(+)
    POSSIBILITIES: (R = ribbon)
                                      |                 |                 |                 |                  |
                                      |                 |                 |                 |                  |
                             0        |        1        |        2        |        3        |        4         |        5
                       R- ------ -R   |   - ------ -    |   R- ------ -   |   R- ------ -   |    - ------ -R   |    - ------ -
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |    |    |        |
                        |        |    |   |        |    |    |        |   |    |        |   |    |        |    |    |        |
                       R- ------ +    |  R- ------ +    |    - ------ +   |   R- ------ +   |   R- ------ +    |    - ------ +

    IN THEORY ONE SHOULD DO:
    plan:
          - group types 0 and 4 -> they have all ribbon or two opposite ribbon & the - opposite to + is non ribbon
                  types 2 and 5 -> they have no ribbon or one that is opposite to cell with +
                  types 1 and 3 -> all the other cases

          - look for 0,1   intersections in types 0 and 4 -> if any intersection is present, it will be with the center
                     0,1,2 intersections in types 2 and 5 -> can be present up to 2 intersections. But we need to check and force intersections to the center when present a ribbon
                     0,1   intersections in types 1 and 3 -> intersections with the cell center will naturally appears

          - put toghether: 0 intersections
                           1 intersections
                           2 intersections

    definitions:
          - group types 0 and 4 -> cells_04
                  types 2 and 5 -> cells_25
                  types 1 and 3 -> cells_13

    IN PRACTISE WE CAN SAVE ALL THE SPLITTING MENTIONED BEFORE BY DOING THE NEXT
    """

    [Fracturelist, Ribbon, mesh, sgndDist_k, float_precision, mac_precision] = Args

    # 1) find when you have an intersection with the cell center - of any subtype
    [indexesFC_T4_central_inters, indexesFC_T4_other_inters] = split_central_from_noncentral_intersections(
        np.asarray(indexesFC_TYPE_4), Fracturelist, mesh, sgndDist_k)

    # 2) split type4 SubType4 from the rest of cells
    [indexesFC_TYPE_4_ST4,indexesFC_TYPE_4_ST01235]=split_type4SubType4_from_rest(np.asarray(indexesFC_T4_other_inters),Fracturelist,mesh,sgndDist_k,Ribbon)


    # 3) force the cell to be at the center if the LS at the center is POSITIVE -> 1 intersection (do not include subtype4)
    [indexesFC_T4_central_inters,
     indexesFC_T4_0_1_2_intersections] = move_intersections_to_the_center_when_inRibbon_type4(indexesFC_T4_central_inters,
                                                                                    indexesFC_TYPE_4_ST01235,
                                                                                    Fracturelist,
                                                                                    mesh,
                                                                                    sgndDist_k)


    # 4) find intersections with the center for forced and non-forced cells
    [T4_x_inters_center,
     T4_y_inters_center,
     T4_edgeORvertexID_center] = find_xy_intersections_with_cell_center(indexesFC_T4_central_inters,
                                                                        Fracturelist,
                                                                        mesh)
    # set the found intersections
    for j in range(len(indexesFC_T4_central_inters)):
        temp_index = indexesFC_T4_central_inters[j]
        x[temp_index ] = [T4_x_inters_center[j]]
        y[temp_index ] = [T4_y_inters_center[j]]
        edgeORvertexID[temp_index ] = [T4_edgeORvertexID_center[j]]
        typeindex[temp_index ] = [1]

    # 5) find 0,1,2 intersections for all the other cells subtypes including subtype4
    #    one assumption is that the front is curved within cells type 4
    #    so there will be always an intersection with both axes whereas within cells type 1 you can have straight front
    #    and thus more checks are needed
    # 0,1,2 intersections
    if len(indexesFC_TYPE_4_ST4)>0:
        indexesFC_T4_0_1_2_intersections = np.concatenate((indexesFC_T4_0_1_2_intersections,np.asarray(indexesFC_TYPE_4_ST4)))
    else : indexesFC_T4_0_1_2_intersections = indexesFC_T4_0_1_2_intersections
    [indexesFC_T4_0_intersection_local,
     indexesFC_T4_1_intersection_local,
     indexesFC_T4_2_intersections_local,
     xCandidate,yCandidate,edge_1_inters,
     xCandidate_2_inter,yCandidate_2_inter,edge_2_inter] = find_xy_intersections_type3_case_0_1_2_intersections(indexesFC_T4_0_1_2_intersections,
                                                                                                                Fracturelist,
                                                                                                                mesh,sgndDist_k,float_precision,mac_precision)
    # set the found intersections
    for j in range(indexesFC_T4_0_intersection_local.size):
        temp_index = indexesFC_T4_0_intersection_local[j]
        x[temp_index ] = []
        y[temp_index ] = []
        edgeORvertexID[temp_index ] = []
        typeindex[temp_index ] = []

    for j in range(indexesFC_T4_1_intersection_local.size):
        temp_index = indexesFC_T4_1_intersection_local[j]
        x[temp_index ] = [xCandidate[j]]
        y[temp_index ] = [yCandidate[j]]
        edgeORvertexID[temp_index ] = [edge_1_inters[j]]
        typeindex[temp_index ] = [0]

    for j in range(indexesFC_T4_2_intersections_local.size):
        temp_index = indexesFC_T4_2_intersections_local[j]
        x[temp_index ] = xCandidate_2_inter[j]
        y[temp_index ] = yCandidate_2_inter[j]
        edgeORvertexID[temp_index ] = edge_2_inter[j]
        typeindex[temp_index ] = [0,0]

    return [ x, y, typeindex, edgeORvertexID]

def get_next_cell_name(current_cell_name,previous_cell_name,FC_type,Args) :
    [mesh,dict_Ribbon,sgndDist_k] = Args
    dict_of_possibilities = {}
    """
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                             0     1      2      3
    """
    if FC_type == 1:
        orientation = define_orientation_type1(current_cell_name, mesh, sgndDist_k)
        if orientation == 0 or orientation == 2 : # quasi-horizontal direction
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][1]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][0]
        else: # quasi-vertical direction
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][3]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][3])] = mesh.NeiElements[current_cell_name][2]
    elif FC_type == 2:
        orientation = define_orientation_type2(current_cell_name, mesh, sgndDist_k)
        if orientation == 0:
            if str(mesh.NeiElements[current_cell_name+1][3]) in dict_Ribbon.keys() and str(current_cell_name) in dict_Ribbon.keys():
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])]=mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][3])]=mesh.NeiElements[current_cell_name][0]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])]=mesh.NeiElements[current_cell_name][1]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])]=mesh.NeiElements[current_cell_name][2]
            else:
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][0]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][2]
        else: # orientation ==1
            if str(mesh.NeiElements[current_cell_name][1]) in dict_Ribbon.keys() and str(mesh.NeiElements[current_cell_name][3]) in dict_Ribbon.keys():
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][0]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][2]
            else:
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][3]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][3])] = mesh.NeiElements[current_cell_name][0]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][1]
                dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][2]
    else:
        if FC_type == 3:
            orientation = define_orientation_type3OR4("3",current_cell_name, mesh, sgndDist_k)
        elif FC_type == 4:
            orientation = define_orientation_type3OR4("4", current_cell_name, mesh, sgndDist_k)
        else: raise SystemExit('Error: Unknown cell type')

        if orientation == 0:
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][0]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][2]
        elif orientation == 1:
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][2])] = mesh.NeiElements[current_cell_name][1]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][2]
        elif orientation == 2:
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][1])] = mesh.NeiElements[current_cell_name][3]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][3])] = mesh.NeiElements[current_cell_name][1]
        elif orientation == 3:
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][0])] = mesh.NeiElements[current_cell_name][3]
            dict_of_possibilities[str(mesh.NeiElements[current_cell_name][3])] = mesh.NeiElements[current_cell_name][0]
        else: raise SystemExit('Error: Wrong orientation')

    try:
        if str(previous_cell_name) not in dict_of_possibilities.keys():
            raise FileNotFoundError
        else:
            return dict_of_possibilities[str(previous_cell_name)]
    except FileNotFoundError:
        print("ERROR: The previous fictitious cell is not neighbour of the current fictitious cell")

def get_next_cell_name_from_first(first_cell_name,FC_type,mesh,sgndDist_k):
    """
    remembrer the usage of NeiElements[i]->[left, right, bottom, up]
                                             0     1      2      3
    """
    if FC_type == 1:
        orientation = define_orientation_type1(first_cell_name, mesh, sgndDist_k)
        if orientation == 0 or orientation == 2 : # quasi-horizontal direction
            next_cell_name = mesh.NeiElements[first_cell_name][0]
        else: # quasi-vertical direction
            next_cell_name = mesh.NeiElements[first_cell_name][2]
    elif FC_type == 2:
        next_cell_name = mesh.NeiElements[first_cell_name][0]
    elif FC_type == 3:
        orientation = define_orientation_type3OR4("3",first_cell_name, mesh, sgndDist_k)
        if orientation == 0 or orientation == 1:
            next_cell_name = mesh.NeiElements[first_cell_name][2]
        else:
            next_cell_name = mesh.NeiElements[first_cell_name][3]
    elif FC_type == 4:
        orientation = define_orientation_type3OR4("4",first_cell_name, mesh, sgndDist_k)
        if orientation == 0 or orientation == 1:
            next_cell_name = mesh.NeiElements[first_cell_name][2]
        else:
            next_cell_name = mesh.NeiElements[first_cell_name][3]
    else: raise SystemExit('Error: Unknown cell type')
    return next_cell_name

from itertools import chain
def itertools_chain_from_iterable(lsts):
    """
    :param lsts: example lsts=[[1],[], [2,3],[4],[],[5,6]]
    :return: [1,2,3,4,5,6]

    It does not work if lsts=[[1],[], [2,3],4,[],[5,6]]
    """
    try :
      to_be_returned =list(chain.from_iterable(lsts))
    except:
      print("ERROR: The list contains an element not between square brakets")
    return to_be_returned

def append_to_typelists(cell_index,cell_type,type1,type2,type3,type4):
    if cell_type == 1:
        type1.append(cell_index)
    elif cell_type == 2:
        type2.append(cell_index)
    elif cell_type == 3:
        type3.append(cell_index)
    elif cell_type == 4:
        type4.append(cell_index)
    return type1,type2,type3,type4

def is_inside_the_triangle(p_center, p_zero_vertex, p1, p2, mac_precision):
    #
    # This function answer to the question:
    # is the point inside a triangle?
    # (given the coordinates)
    T1x = np.asarray([p_center.x,p1.x,p2.x])
    T1y = np.asarray([p_center.y,p1.y,p2.y])
    T2x = np.asarray([p_center.x,p1.x,p_zero_vertex.x])
    T2y = np.asarray([p_center.y,p1.y,p_zero_vertex.y])
    T3x = np.asarray([p_center.x,p2.x,p_zero_vertex.x])
    T3y = np.asarray([p_center.y,p2.y,p_zero_vertex.y])
    Tx = np.asarray([p1.x,p2.x,p_zero_vertex.x])
    Ty = np.asarray([p1.y,p2.y,p_zero_vertex.y])
    if    copute_area_of_a_closed_front(T1x, T1y) \
        + copute_area_of_a_closed_front(T2x, T2y) \
        + copute_area_of_a_closed_front(T3x, T3y) \
        - copute_area_of_a_closed_front(Tx, Ty) < mac_precision:
        return True
    else:
        return False

def recompute_LS_at_tip_cells(sgndDist_k, p_zero_vertex, p_center, p1, p2, mac_precision):
    # find the distance from the cell center to the front
    distance_center_to_front = pointtolinedistance(p1, p2, p_center)

    # we do not allow to have LS == 0
    if distance_center_to_front == 0 :
        distance_center_to_front = -mac_precision
    else :
        """
        Now we want to understand if the sign of the LS at the cell center is positive or negative.
        This question is equivalent of asking if the center of the cell is inside or outside of the fracture.
        Again, the latter question is equivalent of asking if the center of the cell belongs to the triangle 
        that is made by considering the zero vertex and the two points of intersection of the front with the cell. 
        If it is true, then the cell center is inside the fracture, otherwise it is outside
        """
        if is_inside_the_triangle(p_center, p_zero_vertex, p1, p2, mac_precision):
            sgndDist_k[p_center.name] = - distance_center_to_front
        else:
            sgndDist_k[p_center.name] = + distance_center_to_front
    return sgndDist_k

def reconstruct_front_continuous(sgndDist_k, anularegion, Ribbon, eltsChannel, mesh,recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge):

        """
        description of the function.

        Args:
            sgndDist_k: vector that contains the distance from the center of the cell to the front. They are negative if the point is inside the fracture otherwise they are positive
            anularegion:name of the cells where we expect to be the front
            Ribbon:     name of the ribbon elements
            mesh:       obj

        Returns:
            tipcells (integers):         -- descriptions.
            nextribboncells (integers):  -- descriptions.
            vertexes (integers):         -- descriptions.
            alphas (float):              -- descriptions.
            orthogonaldistances (float): -- descriptions.

        """

        recompute_front = False
        float_precision = np.float64
        integer_precision = int
        mac_precision = 10*np.finfo(float).eps
        """
        a := diagnal of the mesh
        b := min size of the front in the cell
        b/a := min_ratio_front_and_edge_size = 0.01
                         ___|_______|__   
                            |      /|
                            |     / |
                            |  a /  |
                            |   /   |
                            |  /    |
                            | /    b/
                         ___|/_____/|___
                            |       |   
        """
        min_ratio_front_and_edge_size = 0.01
        area_of_a_cell = mesh.hx * mesh.hy

        """
        0) - Set all the LS==0 to -mac_precision
        In this way we avoid to deal with the situations where the front is crossing exactly a vertex of an i     
        """
        zerovertexes = np.where(sgndDist_k == 0)[0]
        if len(zerovertexes) > 0:
            sgndDist_k[zerovertexes] = -mac_precision
        del zerovertexes


        """
        1) - define a dictionary for the Ribbon cells
           - find a list of valid fictitius cells (inamesOfFC) that can belongs to more than one fracture
           - compute the LS at the valid fictitius cells (LSofFC)
           - compute the "i names" of the FC of different types 
               Whe define the fictitius cell types:

            type 1        |   type 2        |    type 3       |    type 4
            2(+) & 2(-)   |   2(+) & 2(-)   |    3(+) & 1(-)  |    3(-) & 1(+)  
            + ------ -    |   + ------ -    |    + ------ -   |    - ------ +         
            |        |    |   |        |    |    |        |   |    |        |
            |        |    |   |        |    |    |        |   |    |        |
            + ------ -    |   - ------ +    |    + ------ +   |    - ------ -
        """
        dict_Ribbon = dict(zip(Ribbon.astype(str).tolist(),np.ones(Ribbon.size).astype(bool).tolist()))
        i_1_2_3_4_names_of_fictitiuscells, number_of_type_2_cells, i_1_2_3_4_FC_type, dict_FC_names = find_fictitius_cells(anularegion, mesh.NeiElements, sgndDist_k)

        """
        2) - define the fractures
        """
        # compute the number of FC
        # each cell of type 1, 3, 4 count as 1, type 2 counts as 2

        NofCells_to_explore = i_1_2_3_4_names_of_fictitiuscells.size + 2*number_of_type_2_cells
        NofCells_explored = 0
        del number_of_type_2_cells, i_1_2_3_4_names_of_fictitiuscells

        list_of_Fracturelists = []
        list_of_Cells_type_1_list = []
        list_of_Cells_type_2_list = []
        list_of_Cells_type_3_list = []
        list_of_Cells_type_4_list = []
        Args = [mesh,dict_Ribbon,sgndDist_k]


        # I require more than 3 cells to define a single fracture
        if NofCells_to_explore > 3 :
            # do until you have explored all the cells
            while NofCells_explored < NofCells_to_explore:
                Fracturelist = []
                Cells_type_1_list = []
                Cells_type_2_list = []
                Cells_type_3_list = []
                Cells_type_4_list = []

                first_cell_name = dict_FC_names[next(iter(dict_FC_names))]
                Fracturelist.append(first_cell_name)
                [Cells_type_1_list, Cells_type_2_list, Cells_type_3_list, Cells_type_4_list] = append_to_typelists(len(Fracturelist)-1, i_1_2_3_4_FC_type[str(first_cell_name)], Cells_type_1_list, Cells_type_2_list, Cells_type_3_list, Cells_type_4_list)
                del dict_FC_names[next(iter(dict_FC_names))]
                NofCells_explored += 1

                next_cell_name = get_next_cell_name_from_first(first_cell_name,i_1_2_3_4_FC_type[str(first_cell_name)],mesh,sgndDist_k)

                while next_cell_name != first_cell_name :

                    NofCells_explored += 1
                    Fracturelist.append(next_cell_name) #now is the last cell in the list but also the current cell

                    # we need this check because it happens that some cells of type i are not in the fictitious cells
                    # in that case compute the type on the fly
                    if str(next_cell_name) not in i_1_2_3_4_FC_type.keys():
                        cell_type = get_fictitius_cell_type(get_LS_on_i_fictitius_cell('iabc',next_cell_name,mesh.NeiElements,sgndDist_k)[0])
                    else: cell_type = i_1_2_3_4_FC_type[str(next_cell_name)]

                    [Cells_type_1_list, Cells_type_2_list, Cells_type_3_list, Cells_type_4_list] = append_to_typelists(len(Fracturelist) - 1, cell_type, Cells_type_1_list, Cells_type_2_list, Cells_type_3_list, Cells_type_4_list)
                    if str(next_cell_name) in dict_FC_names.keys():
                        del dict_FC_names[str(next_cell_name)]
                    previous_cell_name = Fracturelist[-2] #second last cell in the list and the one where we are coming
                    next_cell_name = get_next_cell_name(next_cell_name,previous_cell_name,cell_type,Args)

                # now we check if the fracture is good or not
                if len(Fracturelist) > 3:
                    list_of_Fracturelists.append(Fracturelist)
                    list_of_Cells_type_1_list.append(Cells_type_1_list)
                    list_of_Cells_type_2_list.append(Cells_type_2_list)
                    list_of_Cells_type_3_list.append(Cells_type_3_list)
                    list_of_Cells_type_4_list.append(Cells_type_4_list)
                else :
                    print("<< I REJECT A POSSIBLE FRCTURE FRONT BECAUSE IS TOO SMALL >>")
                    print("set the LS of the positive cells to be -machine precision")
                    all_cells_of_all_FC_of_this_small_fracture = np.unique(
                        np.ndarray.flatten(get_fictitius_cell_all_names(np.asarray(Fracturelist), mesh.NeiElements)))
                    index_of_positives = np.where(sgndDist_k[all_cells_of_all_FC_of_this_small_fracture] > 0)[0]
                    sgndDist_k[all_cells_of_all_FC_of_this_small_fracture[index_of_positives]] = -mac_precision
                    del index_of_positives, all_cells_of_all_FC_of_this_small_fracture
            if len(list_of_Fracturelists)<1:
                raise SystemExit('ERROR: not valid fractures have been found! Rememnber that you could have several fractures of too small size to be tracked')
        else :
            raise SystemExit('ERROR: not enough cells to define evene one fracture front!')

        del dict_FC_names, next_cell_name, previous_cell_name, Args, Fracturelist, Cells_type_1_list, Cells_type_2_list, Cells_type_3_list, Cells_type_4_list
        del NofCells_explored, NofCells_to_explore, first_cell_name, dict_Ribbon,  i_1_2_3_4_FC_type

        # plot found sets of ribbon cells
        # fig1 = plot_cells(anularegion, mesh, sgndDist_k, Ribbon, list_of_Fracturelists[0])
        # for j in list_of_Fracturelists:
        #     plot_cells(anularegion, mesh, sgndDist_k, Ribbon, j,fig=fig1)
        # del j, fig1

        #fig1 = plot_cells(anularegion, mesh, sgndDist_k, Ribbon, Fracturelist, None, True)


        # Important check: the region where the LS has been calculated might be not enough in order to
        # reconstruct the front, so we require that the values of the LS at the fictitius cell do not have to be NaN or +1e50
        cells_around_front = np.unique(np.ndarray.flatten(get_fictitius_cell_all_names(itertools_chain_from_iterable(list_of_Fracturelists), mesh.NeiElements)))
        LS_on_cells_around_front = sgndDist_k[cells_around_front]
        if np.any(LS_on_cells_around_front == np.NaN) or  np.any(LS_on_cells_around_front > 10.**40):
            print('WARNING: I am increasing the thickness of the band')
            correct_size_of_pstv_region = False
            return  None, None, None, None, None, None, None, None, correct_size_of_pstv_region, sgndDist_k
        else:
            del cells_around_front, LS_on_cells_around_front

            """
            3) - process fracture fronts
            
            to be output at the end:
            """

            list_of_xintersection_for_all_closed_paths = []
            list_of_yintersection_for_all_closed_paths = []
            list_of_typeindex_for_all_closed_paths = []
            list_of_edgeORvertexID_for_all_closed_paths = []


            for j in range(len(list_of_Fracturelists)):
                if recompute_front: break
                #for j in range(0,1):
                Fracturelist = list_of_Fracturelists[j]
                typeindex = Fracturelist.copy()
                edgeORvertexID = Fracturelist.copy()
                x = Fracturelist.copy()
                y = Fracturelist.copy()

                Args = [np.asarray(Fracturelist), Ribbon, mesh, sgndDist_k, float_precision, mac_precision]

                indexesFC_TYPE_1 = list_of_Cells_type_1_list[j]
                indexesFC_TYPE_2 = list_of_Cells_type_2_list[j]
                indexesFC_TYPE_3 = list_of_Cells_type_3_list[j]
                indexesFC_TYPE_4 = list_of_Cells_type_4_list[j]

                if len(indexesFC_TYPE_3) > 0:
                    [x, y, typeindex, edgeORvertexID] = process_fictitius_cells_3(indexesFC_TYPE_3, Args, x, y, typeindex, edgeORvertexID)

                if len(indexesFC_TYPE_1) > 0:
                    [x, y, typeindex, edgeORvertexID] = process_fictitius_cells_1(indexesFC_TYPE_1, Args, x, y, typeindex,edgeORvertexID)

                if len(indexesFC_TYPE_4) > 0:
                    [x, y, typeindex, edgeORvertexID] = process_fictitius_cells_4(indexesFC_TYPE_4, Args, x, y, typeindex,edgeORvertexID)
                if len(indexesFC_TYPE_2) > 0:
                    #[x, y, typeindex, edgeORvertexID] = process_fictitius_cells_2(indexesFC_TYPE_4, Args, x, y, typeindex,edgeORvertexID)
                    raise SystemExit('ERROR: type 2 to be tested')

                del indexesFC_TYPE_1, indexesFC_TYPE_2, indexesFC_TYPE_3, indexesFC_TYPE_4, Args
                """
                vocabulary:
                xintersection:= x coordinates
                yintersection:= y coordinates
                typeindex:= 0 if node intersecting an edge, 1 if intersecting an existing vertex of the mesh
                edgeORvertexID:= index of the vertex or index of the edge 
                """
                xintersection = itertools_chain_from_iterable(x)
                yintersection = itertools_chain_from_iterable(y)
                # if j==0: fig=None
                # fig = plot_xy_points(anularegion, mesh, sgndDist_k, Ribbon, xintersection, yintersection, fig)
                typeindex = itertools_chain_from_iterable(typeindex)
                edgeORvertexID = itertools_chain_from_iterable(edgeORvertexID)
                del x,y

                """
                The closed front area is implicitly not smaller than 1/2 the area of the cell
                Now we impose a threshold: the area of a closed front should be > area of a cell
                - Compute the front area.
                - If the area > area cell => - find the names of the positive cells
                                             - set the level set of the positive cells artificially to be -mac precision       
                """
                closed_front_area=copute_area_of_a_closed_front(np.asarray(xintersection),np.asarray(yintersection))
                if closed_front_area <= area_of_a_cell*1.01:
                    print("A small front of area ="+str(100*closed_front_area/area_of_a_cell)[:4]+"% of the single cell has been deleted")
                    # set the level set of all the positive cells in fracture list to be positive
                    all_cells_of_all_FC_of_this_small_fracture = np.unique(np.ndarray.flatten(get_fictitius_cell_all_names(np.asarray(Fracturelist), mesh.NeiElements)))
                    index_of_positives = np.where(sgndDist_k[all_cells_of_all_FC_of_this_small_fracture]>0)[0]
                    sgndDist_k[all_cells_of_all_FC_of_this_small_fracture[index_of_positives]] = -mac_precision
                    del index_of_positives, all_cells_of_all_FC_of_this_small_fracture
                    recompute_front = True
                else :
                    list_of_xintersection_for_all_closed_paths.append(xintersection)
                    list_of_yintersection_for_all_closed_paths.append(yintersection)
                    list_of_typeindex_for_all_closed_paths.append(typeindex)
                    list_of_edgeORvertexID_for_all_closed_paths.append(edgeORvertexID)


            # plot reconstructed front
            # fig1 = plot_xy_points(anularegion, mesh, sgndDist_k, Ribbon, list_of_xintersection_for_all_closed_paths[0], list_of_yintersection_for_all_closed_paths[0], fig=None)
            # for j in range(len(list_of_xintersection_for_all_closed_paths)):
            #     fig1 = plot_xy_points(anularegion, mesh, sgndDist_k, Ribbon, list_of_xintersection_for_all_closed_paths[j], list_of_yintersection_for_all_closed_paths[j], fig1)
            # del j, fig1

            global_list_of_TIPcells = []
            global_list_of_TIPcellsONLY = []
            global_list_of_distances = []
            global_list_of_angles = []
            global_list_of_newRibbon = []
            global_list_of_vertexpositionwithinthecell = []
            global_list_of_vertexpositionwithinthecellTIPcellsONLY = []
            sgndDist_k_new = np.copy(sgndDist_k)
            """
            We need to compute first all the closed contours because is of fundamental importance the notion of
            inside or outside of the fracture for what will follow next 
            """
            if not recompute_front:
                for j in range(len(list_of_Fracturelists)):

                    xintersection  = list_of_xintersection_for_all_closed_paths[j]
                    yintersection  = list_of_yintersection_for_all_closed_paths[j]
                    typeindex      = list_of_typeindex_for_all_closed_paths[j]
                    edgeORvertexID = list_of_edgeORvertexID_for_all_closed_paths[j]

                    """
                    4) - Cleaning up the points
                         Make a 2D table where to store info for each node found at the front. 
                         The 1st column contains the TIPcell's name common with the 
                         previous node in the list of nodes at the front while the second column the cell's name common with the next node.
                         The nodes that have to be deleted will have same value in both columns
                        
                         ___|__________|___   
                            |   in     |
                            |         /|
                            |\       / |
                         ___|_\_____/__|___
                            |          |
                            |    out   |  
                    """
                    """
                    new cleaning: 
                    clean only if the elements belong to the same edge
                    """
                    edges_indexes=np.where(np.asarray(typeindex) == 0)[0]
                    indicies_of_repeated_in_edges_indexes = find_indexes_repeatd_elements( np.asarray(edgeORvertexID)[edges_indexes])
                    repeated_indicies = np.sort(edges_indexes[indicies_of_repeated_in_edges_indexes])
                    if repeated_indicies.size > 0:
                        for jjj in range(repeated_indicies.size):
                            value = repeated_indicies[jjj]
                            del xintersection[value-jjj]
                            del yintersection[value-jjj]
                            del typeindex[value-jjj]
                            del edgeORvertexID[value-jjj]
                        recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge = True
                        print("deleted "+str(repeated_indicies.size)+" points")
                        del jjj, value, indicies_of_repeated_in_edges_indexes, repeated_indicies, edges_indexes

                    """
                    new cleaning: 
                    Before going further we need to collapse to the closest mesh node all the edges of the front that are very small
                    """
                    # compute all the distances between the vertexes at the front and check if some of them are smaller than the tollerance
                    # x_temp = np.asarray(xintersection)
                    # y_temp = np.asarray(yintersection)
                    # shifted_range = list(range(1,len(xintersection)))
                    # shifted_range.append(0)
                    # dxdx = np.square( x_temp[0:len(xintersection)] - x_temp[shifted_range])
                    # dydy = np.square( y_temp[0:len(yintersection)] - y_temp[shifted_range])
                    # Lcheck = np.sqrt( dxdx + dydy ) / np.sqrt(mesh.hx**2 + mesh.hy**2) < min_ratio_front_and_edge_size
                    # indexes_of_points_to_be_collapsed = np.where (Lcheck == True)
                    # x_points_to_be_collapsed = x_temp[points_to_be_collapsed]
                    # y_points_to_be_collapsed = y_temp[points_to_be_collapsed]

                    # standar cleaning
                    nodeVScommonelementtable=np.zeros([len(xintersection), 3],dtype=int)
                    for nodeindex in range(0,len(xintersection)):
                        # commonbackward contains the unique values in cellOfNodei that are in cellOfNodeim1.
                        # element -1 of a list is the last element
                        commonbackward = findcommon(nodeindex, (nodeindex - 1), typeindex, mesh.Connectivityedgeselem, mesh.Connectivitynodeselem, edgeORvertexID)
                        # commonforward contains the unique values in cellOfNodei that are in cellOfNodeip1.
                        # when nodeindex == len(xintersection)-1 then (nodeindex + 1)%len(xintersection)==0
                        commonforward = findcommon(nodeindex, (nodeindex + 1)%len(xintersection), typeindex, mesh.Connectivityedgeselem, mesh.Connectivitynodeselem, edgeORvertexID)
                        column=0
                        nodeVScommonelementtable, exitstatus=filltable(nodeVScommonelementtable,nodeindex,commonbackward,sgndDist_k,column)
                        if not exitstatus:
                            raise SystemExit('ERROR: two consecutive nodes does not belongs to a common cell')
                        column=1
                        nodeVScommonelementtable, exitstatus=filltable(nodeVScommonelementtable,nodeindex,commonforward,sgndDist_k,column)
                        if not exitstatus:
                            raise SystemExit('ERROR: two consecutive nodes does not belongs to a common cell')

                    listofTIPcells = []
                    # remove the nodes in the cells with more than 2 nodes and keep the first and the last node
                    # counter = 0
                    # n=len(xintersection)
                    # jump = False
                    for nodeindex in range(0, len(xintersection)):
                        # if nodeVScommonelementtable[nodeindex][1] == nodeVScommonelementtable[nodeindex][0]:
                        #     # plot before removing
                        #     # A = np.full(mesh.NumberOfElts, np.nan)
                        #     # A[anularegion] = sgndDist_k[anularegion]
                        #     # from visualization import plot_fracture_variable_as_image
                        #     # figure = plot_fracture_variable_as_image(A, mesh)
                        #     # ax = figure.get_axes()[0]
                        #     # xtempppp = xintersection
                        #     # ytempppp = yintersection
                        #     # xtempppp.append(xtempppp[0]) # close the front
                        #     # ytempppp.append(ytempppp[0]) # close the front
                        #     # plt.plot(xtempppp, ytempppp, '-o')
                        #     # plt.plot( xintersection[nodeindex-counter - 1:nodeindex-counter + 1], yintersection[nodeindex-counter - 1:nodeindex-counter + 1], '-r')
                        #     # plt.plot(xblack, yblack, '.',color='black')
                        #     # plt.plot(mesh.CenterCoor[Ribbon,0], mesh.CenterCoor[Ribbon,1], '.',color='g')
                        #     # plt.plot(mesh.CenterCoor[listofTIPcells, 0] + mesh.hx / 10, mesh.CenterCoor[listofTIPcells, 1] + mesh.hy / 10, '.', color='blue')
                        #
                        #     del xintersection[nodeindex-counter]
                        #     del yintersection[nodeindex-counter]
                        #     del typeindex[nodeindex-counter]
                        #     del edgeORvertexID[nodeindex-counter]
                        #
                        #     nodeVScommonelementtable[nodeindex][2]=1 # to remember that the node has been deleted
                        #
                        #     #plot after removing
                        #     # A = np.full(mesh.NumberOfElts, np.nan)
                        #     # A[anularegion] = sgndDist_k[anularegion]
                        #     # from visualization import plot_fracture_variable_as_image
                        #     # figure = plot_fracture_variable_as_image(A, mesh)
                        #     # ax = figure.get_axes()[0]
                        #     # xtempppp = xintersection
                        #     # ytempppp = yintersection
                        #     # xtempppp.append(xtempppp[0])  # close the front
                        #     # ytempppp.append(ytempppp[0])  # close the front
                        #     # plt.plot(xtempppp, ytempppp, '-o')
                        #     # plt.plot(xintersection[nodeindex-counter - 1:nodeindex-counter + 1], yintersection[nodeindex-counter - 1:nodeindex-counter + 1], '-r')
                        #     # plt.plot(xblack, yblack, '.', color='black')
                        #     # plt.plot(mesh.CenterCoor[Ribbon, 0], mesh.CenterCoor[Ribbon, 1], '.', color='g')
                        #     # plt.plot(mesh.CenterCoor[listofTIPcells, 0] + mesh.hx / 10,
                        #     #          mesh.CenterCoor[listofTIPcells, 1] + mesh.hy / 10, '.', color='blue')
                        #     counter = counter + 1
                        # elif nodeVScommonelementtable[nodeindex][0] == nodeVScommonelementtable[(nodeindex+1)%n][1]:
                        #     # plot before removing
                        #     # A = np.full(mesh.NumberOfElts, np.nan)
                        #     # A[anularegion] = sgndDist_k[anularegion]
                        #     # from visualization import plot_fracture_variable_as_image
                        #     # figure = plot_fracture_variable_as_image(A, mesh)
                        #     # ax = figure.get_axes()[0]
                        #     # xtempppp = xintersection
                        #     # ytempppp = yintersection
                        #     # xtempppp.append(xtempppp[0]) # close the front
                        #     # ytempppp.append(ytempppp[0]) # close the front
                        #     # plt.plot(xtempppp, ytempppp, '-o')
                        #     # plt.plot( xintersection[nodeindex-counter - 1:nodeindex-counter + 1], yintersection[nodeindex-counter - 1:nodeindex-counter + 1], '-r')
                        #     # plt.plot(xblack, yblack, '.',color='black')
                        #     # plt.plot(mesh.CenterCoor[Ribbon,0], mesh.CenterCoor[Ribbon,1], '.',color='g')
                        #     # plt.plot(mesh.CenterCoor[listofTIPcells, 0] + mesh.hx / 10, mesh.CenterCoor[listofTIPcells, 1] + mesh.hy / 10, '.', color='blue')
                        #     del xintersection[nodeindex-counter]
                        #     del yintersection[nodeindex-counter]
                        #     del typeindex[nodeindex-counter]
                        #     del edgeORvertexID[nodeindex-counter]
                        #     nodeVScommonelementtable[nodeindex][2]=1 # to remember that the node has been deleted
                        #     counter = counter + 1
                        #     del xintersection[(nodeindex-counter+1)%len(xintersection)]
                        #     del yintersection[(nodeindex-counter+1)%len(xintersection)]
                        #     del typeindex[(nodeindex-counter+1)%len(xintersection)]
                        #     del edgeORvertexID[(nodeindex-counter+1)%len(xintersection)]
                        #     nodeVScommonelementtable[(nodeindex+1)%n][2]=1 # to remember that the node has been deleted
                        #     counter = counter + 1
                        #     jump = True
                        #     # plot after removing
                        #     # A = np.full(mesh.NumberOfElts, np.nan)
                        #     # A[anularegion] = sgndDist_k[anularegion]
                        #     # from visualization import plot_fracture_variable_as_image
                        #     # figure = plot_fracture_variable_as_image(A, mesh)
                        #     # ax = figure.get_axes()[0]
                        #     # xtempppp = xintersection
                        #     # ytempppp = yintersection
                        #     # xtempppp.append(xtempppp[0])  # close the front
                        #     # ytempppp.append(ytempppp[0])  # close the front
                        #     # plt.plot(xtempppp, ytempppp, '-o')
                        #     # plt.plot(xintersection[nodeindex-counter - 1:nodeindex-counter + 1], yintersection[nodeindex-counter - 1:nodeindex-counter + 1], '-r')
                        #     # plt.plot(xblack, yblack, '.', color='black')
                        #     # plt.plot(mesh.CenterCoor[Ribbon, 0], mesh.CenterCoor[Ribbon, 1], '.', color='g')
                        #     # plt.plot(mesh.CenterCoor[listofTIPcells, 0] + mesh.hx / 10,
                        #     #          mesh.CenterCoor[listofTIPcells, 1] + mesh.hy / 10, '.', color='blue')
                        # else:
                        #     if jump:
                        #         jump = False
                        #     else:
                        #         listofTIPcells.append(nodeVScommonelementtable[nodeindex][0])
                        listofTIPcells.append(nodeVScommonelementtable[nodeindex][0])
                    # del n, jump, nodeindex, counter

                    # In principle the following check should be activated only if the front is
                    # approaching the same tip cell. The strategy is to set these shared tip cells to be negative and re-launch the code
                    # At this stage if we find duplicated cells in the tip cells, than that means we should
                    # impose the level set value to -machine precision in those cells and recompute the whole fractures
                    # It means that we have some coalescence.

                    # if j==0: fig=None
                    # fig = plot_xy_points(anularegion, mesh, sgndDist_k, Ribbon, xintersection, yintersection, fig)
                    u, c = np.unique(np.asarray(listofTIPcells), return_counts=True)
                    dup = u[c > 1]

                    if dup.size > 1:
                        recompute_front = True
                        # set the repeated cells artificially inside the fracture
                        print("- Recomputing the fracture front because one or more coalescing point have been found")
                        print("set the repeated cells artificially inside the fracture: volume error equal to " + str(dup.size) + " cells")
                        sgndDist_k[dup] = -mac_precision
                        break  # break here

                    """
                    5) - find zero vertexes, find alphas & distances 
                         Define the correct node from where compute the distance to the front
                         that node has the largest distance from the front and is inside the fracture but belongs to the tip cell  
                    """
                    vertexpositionwithinthecell=[0 for i in range(len(listofTIPcells))]
                    vertexID = [0 for i in range(len(listofTIPcells))] #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                    distances = [0 for i in range(len(listofTIPcells))]
                    angles = [0 for i in range(len(listofTIPcells))]
                    xintersectionsfromzerovertex = []  #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                    yintersectionsfromzerovertex = []  #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING

                    # loop over the all segments at the fracture front
                    # the number of segments is equal to the number of tipcells because the front is closed
                    for nodeindex in range(0, len(xintersection)):
                        nodeindexp1 = (nodeindex + 1)%len(xintersection) # take the near vertex to define an edge
                        localvertexID = []
                        localdistances = []
                        localvertexpositionwithinthecell = []
                        p = Point(0,0.,0.)
                        i=listofTIPcells[nodeindexp1]
                        # check the vertexes if they are inside or outside of the fracture
                        answer_on_vertexes = ISinsideFracture(i, mesh, sgndDist_k)
                        for jj in range(0,4):
                            if answer_on_vertexes[jj]: # if the vertex is inside the fracture
                                p.name = mesh.Connectivity[i][jj]
                                p.x = mesh.VertexCoor[p.name][0]
                                p.y = mesh.VertexCoor[p.name][1]
                                localvertexID.append(p.name)
                                localvertexpositionwithinthecell.append(jj)
                                p1 = Point(0,xintersection[nodeindex], yintersection[nodeindex])
                                p2 = Point(0,xintersection[nodeindexp1], yintersection[nodeindexp1])
                                localdistances.append(pointtolinedistance(p1, p2, p)) #compute the distance from the vertex to the front

                        # take the largest distance from the front
                        if len(localdistances)==0:
                            raise SystemExit('ERROR: there are no nodes in the given tip cell that are inside the fracture')
                        index = np.argmax(np.asarray(localdistances)) # compute the index of the point with the maximun distance to the front
                        if index.size>1: # if you have two nodes that have the same distance to the front and are inside thake the first
                            index = index[0]

                        # take:
                        #       - name of the vertex
                        #       - local position within the cell
                        #       - distance to the front
                        vertexID[nodeindexp1]=localvertexID[index] #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                        vertexpositionwithinthecell[nodeindexp1]=localvertexpositionwithinthecell[index]
                        distances[nodeindexp1]=localdistances[index]

                        # compute the angle
                        x = mesh.VertexCoor[localvertexID[index]][0] # x coordinate of the zero vertex
                        y = mesh.VertexCoor[localvertexID[index]][1] # y coordinate of the zero vertex
                        [angle, xint, yint] = findangle(xintersection[nodeindex], yintersection[nodeindex], xintersection[nodeindexp1], yintersection[nodeindexp1], x, y)
                        angles[nodeindexp1] = angle
                        #[angle, xint, yint] = findangle(xintersection[nodeindex], yintersection[nodeindex],
                        #                                xintersection[nodeindexp1], yintersection[nodeindexp1], mesh.CenterCoor[i,0], mesh.CenterCoor[i,1])  #<--------- IT CAN BE REMOVED, IT IS ONLY FOR ONE POSSIBLE LOCAL DEBUGGING
                        if recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge:
                            p_zero_vertex = Point(0, x, y)
                            p_center = Point(i, mesh.CenterCoor[i,0], mesh.CenterCoor[i,1])
                            p1 = Point(2, xintersection[nodeindex], yintersection[nodeindex])
                            p2 = Point(3, xintersection[nodeindexp1], yintersection[nodeindexp1])
                            sgndDist_k_new = recompute_LS_at_tip_cells(sgndDist_k_new, p_zero_vertex, p_center,p1,p2, mac_precision)
                        xintersectionsfromzerovertex.append(xint) #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                        yintersectionsfromzerovertex.append(yint) #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING

                    if recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge: del p_zero_vertex, p_center, p1, p2
                    listofTIPcellsONLY=np.asarray(listofTIPcells,dtype=int) # It contains only the tip cells, not the one fully traversed
                    vertexpositionwithinthecellTIPcellsONLY = np.asarray(vertexpositionwithinthecell,dtype=int)
                    # distancesTIPcellsONLY=np.copy(distances) #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                    # anglesTIPcellsONLY=np.copy(angles)       #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING
                    # vertexIDTIPcellsONLY=np.copy(vertexID)   #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING


                    # find the new ribbon cells
                    newRibbon = np.unique(np.ndarray.flatten(mesh.NeiElements[listofTIPcellsONLY, :]))
                    temp = sgndDist_k[newRibbon]
                    temp[temp > 0] = 0
                    newRibbon = newRibbon[np.nonzero(temp)]
                    newRibbon = np.setdiff1d(newRibbon, np.asarray(listofTIPcellsONLY))

                    if len(xintersection)==0:
                        raise SystemExit('ERROR: front not reconstructed')

                    # A = np.full(mesh.NumberOfElts, np.nan)
                    # A[anularegion] = sgndDist_k[anularegion]
                    # from visualization import plot_fracture_variable_as_image
                    # figure = plot_fracture_variable_as_image(A, mesh)
                    # ax = figure.get_axes()[0]
                    # xtemp = xintersection
                    # ytemp = yintersection
                    # xtemp.append(xtemp[0]) # close the front
                    # ytemp.append(ytemp[0]) # close the front
                    # # plt.plot(mesh.CenterCoor[listofTIPcells, 0], mesh.VertexCoor[mesh.Connectivity[Ribbon,0],1], '.',color='violet')
                    # plt.plot(xtemp, ytemp, '-o')
                    # n=len(xintersectionsfromzerovertex)
                    # for i in range(0,n) :
                    #     plt.plot([mesh.VertexCoor[vertexID[(i+1)%n], 0], xintersectionsfromzerovertex[i]], [mesh.VertexCoor[vertexID[(i+1)%n], 1], yintersectionsfromzerovertex[i]], '-r')
                          ##plt.plot([mesh.CenterCoor[listofTIPcells[(i+1)%n], 0], xintersectionsfromzerovertex[i]],[mesh.CenterCoor[listofTIPcells[(i+1)%n], 1], yintersectionsfromzerovertex[i]], '-r')
                    # # plt.plot(xred, yred, '.',color='red' )
                    # # plt.plot(xgreen, ygreen, '.',color='yellow')
                    # # plt.plot(xblack, yblack, '.',color='black')
                    # plt.plot(mesh.CenterCoor[newRibbon,0], mesh.CenterCoor[newRibbon,1], '.',color='orange')
                    # #plt.plot(mesh.CenterCoor[Ribbon,0], mesh.CenterCoor[Ribbon,1], '.',color='b')
                    # plt.plot(mesh.CenterCoor[listofTIPcells, 0] + mesh.hx / 10, mesh.CenterCoor[listofTIPcells, 1] + mesh.hy / 10, '.', color='blue')
                    # plt.plot(mesh.VertexCoor[vertexID, 0], mesh.VertexCoor[vertexID, 1], '.', color='red')
                    # plt.plot(xintersectionsfromzerovertex, yintersectionsfromzerovertex, '.', color='red')

                    # from utility import plot_as_matrix
                    # K = np.zeros((mesh.NumberOfElts,), )
                    # K[listofTIPcells] = angles
                    # plot_as_matrix(K, mesh)

                    # from utility import plot_as_matrix
                    # K = np.zeros((mesh.NumberOfElts,), )
                    # K[listofTIPcells] = distances
                    # plot_as_matrix(K, mesh)

                    # from utility import plot_as_matrix
                    # K = np.zeros((Fr_kplus1.mesh.NumberOfElts,), )
                    # K[Fr_kplus1.EltTip] = Fr_kplus1.alpha
                    # plot_as_matrix(K, Fr_kplus1.mesh)

                    # from utility import plot_as_matrix
                    # K = np.zeros((Fr_kplus1.mesh.NumberOfElts,), )
                    # K[Fr_kplus1.EltTip] = Fr_kplus1.ZeroVertex
                    # plot_as_matrix(K, Fr_kplus1.mesh)

                    # from utility import plot_as_matrix
                    # K = np.zeros((Fr_lstTmStp.mesh.NumberOfElts,), )
                    # K[EltTip_k] = zrVertx_k
                    # plot_as_matrix(K, Fr_lstTmStp.mesh)

                    # mesh.identify_elements(listofTIPcellsONLY)
                    # test=listofTIPcellsONLY
                    # test1=listofTIPcellsONLY
                    # for j in range(1,len(listofTIPcellsONLY)):
                    #     element=listofTIPcellsONLY[j]
                    #     test1[j]=mesh.Connectivity[element][vertexpositionwithinthecellTIPcellsONLY[j]]
                    #     test[j]=vertexIDTIPcellsONLY[j]-mesh.Connectivity[element][vertexpositionwithinthecellTIPcellsONLY[j]]
                    # from utility import plot_as_matrix
                    # K = np.zeros((mesh.NumberOfElts,), )
                    # K[listofTIPcellsONLY] = test1
                    # plot_as_matrix(K, mesh)

                    global_list_of_TIPcells.extend(listofTIPcells)
                    global_list_of_TIPcellsONLY.extend(listofTIPcellsONLY.tolist()) #np
                    global_list_of_distances.extend(distances)
                    global_list_of_angles.extend(angles)
                    global_list_of_newRibbon.extend(newRibbon.tolist()) #np
                    global_list_of_vertexpositionwithinthecell.extend(vertexpositionwithinthecell)
                    global_list_of_vertexpositionwithinthecellTIPcellsONLY.extend(vertexpositionwithinthecellTIPcellsONLY.tolist()) #np



            if not recompute_front:
                """
                6) - find fully traversed elements and their alphas & distances 
                """
                # find the cells that have been passed completely by the front [CCPbF]
                # you can find them by this reasoning:
                #
                # [CCPbF] = [cells where LS<0] - [cells at the previous channell (meaning ribbon+fracture)] - [tip cells]
                #
                # "-" means: "take away the names of"
                #
                # this is not enough, we need to account for positive cells that have been excluded from drowing the front because
                # it was having to high curvature within it. In order to find the cells I am speaking about we can use the folowing reasoning.
                #
                # [CCPbF] = [CCPbF] + neighbours of [CCPbF] - [cells at the previous channell (meaning ribbon+fracture)]  - [tip cells]
                #


                # update the levelset with the distance at the tip cells according to the distance to the reconstructed front
                # this is important in order to proper estimate the distance to the front of the fully traversed cells
                # this should not be done if we discover that we have coalescence and we would need to recompute the front location
                # according with a LS thats why we make a copy of the original sgndDist_k and we will restore it in case we see
                # that we have coalescence
                original_sgndDist_k = np.copy(sgndDist_k)
                sgndDist_k = sgndDist_k_new

                temp = sgndDist_k[range(0, len(sgndDist_k))]
                temp[temp > 0] = 0
                negative_cells = np.nonzero(temp)[0]
                fullyfractured = np.setdiff1d(negative_cells, eltsChannel)
                fullyfractured = np.setdiff1d(fullyfractured, np.asarray(global_list_of_TIPcells))
                positivefullyfractured = np.setdiff1d(np.unique(np.ndarray.flatten(mesh.NeiElements[fullyfractured])), np.asarray(global_list_of_TIPcells))
                positivefullyfractured = np.setdiff1d(positivefullyfractured, fullyfractured)
                positivefullyfractured = np.setdiff1d(positivefullyfractured, eltsChannel)
                if len(positivefullyfractured)>0:
                    fullyfractured = np.concatenate((fullyfractured,positivefullyfractured))
                    negative_cells = np.concatenate((negative_cells,positivefullyfractured))

                [left_elem, right_elem, bottom_elem, top_elem] = [0, 1, 2, 3]

                if len(fullyfractured) > 0:
                    if recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge:
                        """
                        If you jum,p here it menas that 
                        previously the Level set at the tip cells have been redefined
                        now we have to recompute the level set in the negative cells
                        because when coalescence is enforced then level set at some cells was set to -machine precision
                        then the front is reconstructed and finally we are here, about to compute the aphas and distances to the front in the 
                        fully traversed cells. We need to really to define the level set in the cells where we set -machine precision
                        """
                        # level set known and unknown, cell names where the LS is known,cracked elements (including tip), mesh , empty, Specific cells that I need inwards
                        SolveFMM(sgndDist_k, np.asarray(global_list_of_TIPcellsONLY), negative_cells, mesh, [], negative_cells)
                        # Usage of SolveFMM:
                        # 1st arg: vector with the LS value everywhere
                        # 2nd arg: list of positions (or cell names) where the LS is KNOWN => it should be a set of closed fronts!
                        # 3rd arg: unknown need ??
                        # 4th arg: mesh obj
                        # 5th arg: name of the cells where to compute the LS => we expect positive LS values here!
                        # 6th arg: name of the cells where to compute the LS => we expect negative LS values here!

                    fullyfractured_angle = []
                    fullyfractured_distance = []
                    fullyfractured_vertexID = []
                    fullyfractured_vertexpositionwithinthecell = []
                    # loop over the fullyfractured cells
                    for fullyfracturedcell in range(0, len(fullyfractured)):
                        i = fullyfractured[fullyfracturedcell]
                        """
                        you are in cell i
                        take the level set at the center of the neighbors cells 
                          _   _   _   _   _   _
                        | _ | _ | _ | _ | _ | _ |
                        | _ | _ | _ | _ | _ | _ |
                        | _ | e | a | f | _ | _ |
                        | _ | _ 3 _ 2 _ | _ | _ |              
                        | _ | d | i | b | _ | _ |
                        | _ | _ 0 _ 1 _ | _ | _ |
                        | _ | h | c | g | _ | _ |
                        | _ | _ | _ | _ | _ | _ |
        
                                                0     1      2      3
                        NeiElements[i]->[left, right, bottom, up]
                        """

                        a = mesh.NeiElements[i, top_elem]
                        b = mesh.NeiElements[i, right_elem]
                        c = mesh.NeiElements[i, bottom_elem]
                        d = mesh.NeiElements[i, left_elem]
                        e = mesh.NeiElements[d, top_elem]
                        f = mesh.NeiElements[b, top_elem]
                        g = mesh.NeiElements[b, bottom_elem]
                        h = mesh.NeiElements[d, bottom_elem]

                        hcid = sgndDist_k[[h, c, i, d]]
                        cgbi = sgndDist_k[[c, g, b, i]]
                        ibfa = sgndDist_k[[i, b, f, a]]
                        diae = sgndDist_k[[d, i, a, e]]
                        LS = [hcid, cgbi, ibfa, diae]
                        hcid_mean = np.mean(np.asarray(sgndDist_k[[h, c, i, d]]))
                        cgbi_mean = np.mean(np.asarray(sgndDist_k[[c, g, b, i]]))
                        ibfa_mean = np.mean(np.asarray(sgndDist_k[[i, b, f, a]]))
                        diae_mean = np.mean(np.asarray(sgndDist_k[[d, i, a, e]]))
                        LS_means = [hcid_mean, cgbi_mean, ibfa_mean, diae_mean]
                        localvertexpositionwithinthecell = np.argmin(np.asarray(LS_means))
                        fullyfractured_vertexpositionwithinthecell.append(localvertexpositionwithinthecell)
                        fullyfractured_distance.append(np.abs(LS_means[localvertexpositionwithinthecell]))
                        fullyfractured_vertexID.append(mesh.Connectivity[i, localvertexpositionwithinthecell])
                        chosenLS = LS[localvertexpositionwithinthecell]
                        # compute the angle
                        dLSdy = 0.5 * mesh.hy * (chosenLS[3] + chosenLS[2] - chosenLS[1] - chosenLS[0])
                        dLSdx = 0.5 * mesh.hx * (chosenLS[2] + chosenLS[1] - chosenLS[3] - chosenLS[0])
                        if dLSdy == 0. and dLSdx != 0.:
                            fullyfractured_angle.append(0.)
                        elif dLSdy != 0. and dLSdx == 0:
                            fullyfractured_angle.append(np.pi())
                        elif dLSdy != 0. and dLSdx != 0:
                            fullyfractured_angle.append(np.arctan(np.abs(dLSdy) / np.abs(dLSdx)))
                        else:
                            raise SystemExit('ERROR minimum of the function has been found, not expected')

                    # finally append these informations to what computed before

                    global_list_of_TIPcells.extend(np.ndarray.tolist(fullyfractured))
                    global_list_of_distances.extend(fullyfractured_distance)
                    global_list_of_angles.extend(fullyfractured_angle)
                    global_list_of_vertexpositionwithinthecell.extend(fullyfractured_vertexpositionwithinthecell)

                    #vertexID = vertexID + fullyfractured_vertexID #<--------- IT CAN BE REMOVED, IT IS ONLY FOR LOCAL DEBUGGING


                # Cells status list store the status of all the cells in the domain
                # update ONLY the position of the tip cells
                CellStatusNew = np.zeros(mesh.NumberOfElts, int)
                CellStatusNew[eltsChannel] = 1
                CellStatusNew[listofTIPcells] = 2
                CellStatusNew[Ribbon] = 3

                # In principle the following check should be activated only if the front is
                # approaching the same tip cell
                # the strategy is to set these shared tip cells to be negative and re-launch the code
                u, c = np.unique(np.asarray(global_list_of_TIPcells), return_counts=True)
                dup = u[c > 1]
                if dup.size > 1:
                    recompute_front = True
                    sgndDist_k = original_sgndDist_k
                    # We compute the front and we come here. This means that the front is entering twice the same cell.
                    # The strategy was to set to -machine precision the level set in those cells
                    # These cells then may become fully traversed and thus the proper calculation of the distance to the front is
                    # needed. In the next front reconstruction we will propagate inward the level set from the tip cells
                    recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge = True
                    # set the repeated cells artificially inside the fracture
                    print("set the repeated cells artificially inside the fracture: volume error equal to " + str(dup.size) + " cells")
                    sgndDist_k[dup]=-mac_precision         #fig1 = plot_cells(anularegion, mesh, sgndDist_k, Ribbon, dup, None, True)
                else: recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge = False

            if recompute_front:
                """
                ##################################################
                #                                                #
                #              RECOMPUTE THE FRONT!              #
                # -because coalescence as been detected          #
                # -because we need to compute LS on more cells   #
                ##################################################
                """
                [global_list_of_TIPcells,
                 global_list_of_TIPcellsONLY,
                 global_list_of_distances,
                 global_list_of_angles,
                 CellStatusNew,
                 global_list_of_newRibbon,
                 global_list_of_vertexpositionwithinthecell,
                 global_list_of_vertexpositionwithinthecellTIPcellsONLY,
                 correct_size_of_pstv_region,sgndDist_k] = reconstruct_front_continuous(sgndDist_k, anularegion, Ribbon, eltsChannel, mesh, recomp_LS_4fullyTravCellsAfterCoalescence_OR_RemovingPtsOnCommonEdge)
            else:
                correct_size_of_pstv_region = True
            return \
                np.asarray(global_list_of_TIPcells),\
                np.asarray(global_list_of_TIPcellsONLY), \
                np.asarray(global_list_of_distances), \
                np.asarray(global_list_of_angles), \
                CellStatusNew, \
                np.asarray(global_list_of_newRibbon), \
                global_list_of_vertexpositionwithinthecell, \
                np.asarray(global_list_of_vertexpositionwithinthecellTIPcellsONLY), \
                correct_size_of_pstv_region,\
                sgndDist_k

def UpdateListsFromContinuousFrontRec(newRibbon, listofTIPcells, sgndDist_k, zrVertx_k, mesh):

        EltChannel_k = np.setdiff1d(np.where(sgndDist_k<0)[0], listofTIPcells)
        EltTip_k = listofTIPcells
        EltCrack_k = np.concatenate((listofTIPcells, EltChannel_k))
        # from utility import plot_as_matrix
        # K = np.zeros((mesh.NumberOfElts,), )
        # K[np.where(sgndDist_k < 0)[0]] = 1
        # K[listofTIPcells] = 2
        # plot_as_matrix(K, mesh)
        if np.unique(EltCrack_k).size != EltCrack_k.size:
            raise SystemExit('ERROR: the front is entering more than 1 time the same cell')
        EltRibbon_k = newRibbon

        # Cells status list store the status of all the cells in the domain
        # update ONLY the position of the tip cells
        CellStatus_k = np.zeros(mesh.NumberOfElts, int)
        CellStatus_k[EltChannel_k] = 1
        CellStatus_k[EltTip_k] = 2
        CellStatus_k[EltRibbon_k] = 3
        # from utility import plot_as_matrix
        # K = np.zeros((mesh.NumberOfElts,), )
        # plot_as_matrix(CellStatus_k, mesh)
        return   EltChannel_k, EltTip_k, EltCrack_k, EltRibbon_k, zrVertx_k, CellStatus_k