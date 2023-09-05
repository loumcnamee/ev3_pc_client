#!/usr/bin/env python3
# experiemnts and tests with occupancy grids

from math import floor
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from scipy.ndimage import rotate
import polarTransform

#import DiffSteer, OccupancyGrid, RangeBearingSensor

# import time
# import keyboard 



def bresenham(p0, p1):
    """
    Line drawing in a grid

    :param p0: initial point
    :type p0: array_like(2) of int
    :param p1: end point
    :type p1: array_like(2) of int
    :return: arrays of x and y coordinates for points along the line
    :rtype: ndarray(N), ndarray(N) of int

    Return x and y coordinate vectors for points in a grid that lie on
    a line from ``p0`` to ``p1`` inclusive.

    * The end points, and all points along the line are integers.
    * Points are always adjacent, but the slope from point to point is not constant.


    Example:

    .. runblock:: pycon

        >>> from spatialmath.base import bresenham
        >>> bresenham((2, 4), (10, 10))

    .. plot::

        from spatialmath.base import bresenham
        import matplotlib.pyplot as plt
        p = bresenham((2, 4), (10, 10))
        plt.plot((2, 10), (4, 10))
        plt.plot(p[0], p[1], 'ok')
        plt.plot(p[0], p[1], 'k', drawstyle='steps-post')
        ax = plt.gca()
        ax.grid()


    .. note:: The API is similar to the Bresenham algorithm but this
        implementation uses NumPy vectorised arithmetic which makes it
        faster than the Bresenham algorithm in Python.
    """
    x0, y0 = p0
    x1, y1 = p1

    dx = x1 - x0
    dy = y1 - y0

    if abs(dx) >= abs(dy):
        # shallow line -45° <= θ <= 45°
        # y = mx + c
        if dx == 0:
            # case p0 == p1
            x = np.r_[x0]
            y = np.r_[y0]
        else:
            m = dy / dx
            c = y0 - m * x0
            if dx > 0:
                # line to the right
                x = np.arange(x0, x1 + 1)
            elif dx < 0:
                # line to the left
                x = np.arange(x0, x1 - 1, -1)
            y = np.round(x * m + c)

    else:
        # steep line  θ < -45°,  θ > 45°
        # x = my + c
        m = dx / dy
        c = x0 - m * y0
        if dy > 0:
            # line to the right
            y = np.arange(y0, y1 + 1)
        elif dy < 0:
            # line to the left
            y = np.arange(y0, y1 - 1, -1)
        x = np.round(y * m + c)

    return np.asarray([x.astype(int), y.astype(int)])


def range_bearing_sample(hdg, bw, bw_res, rng, rng_max, rng_res):
    """ return an array representing the occupancy values of a range-bearing sensor
        bw = sensor effective beamwidth in degrees
        rng = range reading in meters
        bw_res = angular resolutioon in degress
        rng_res = range resolution in meters
    """ 
    rad2deg = np.pi/180
    
    range_cells_max = floor(rng_max/rng_res)
    range_cells = floor(rng/rng_res)
    brg_cells = floor(bw/bw_res)
    center_angle = hdg*rad2deg
    left_angle = center_angle + (bw*rad2deg/2)
    # if left_angle < 0:
    #     left_angle = left_angle + np.pi*2
    right_angle = center_angle - (bw*rad2deg/2)
    # if right_angle < 0:
    #     right_angle = right_angle + np.pi*2

    left_beam_extent = [range_cells_max*np.cos(left_angle), range_cells_max*np.sin(left_angle)]
    center_beam_extent = [range_cells_max*np.cos(center_angle), range_cells_max*np.sin(center_angle)]
    right_beam_extent = [range_cells_max*np.cos(right_angle), range_cells_max*np.sin(right_angle)]
    beam_origin = [0, 0]
    beam = np.array([beam_origin, left_beam_extent, center_beam_extent, right_beam_extent])

    #beam=np.transpose(beam)
    #print(beam)

    # reading = np.full((range_cells_max, 1),0.5)
    # reading[0:range_cells-2] = 0.0
    # reading[range_cells-2:range_cells+3] = np.array([[0.1], [0.3], [0.6], [0.9], [0.9] ])
    
    #print(left_angle, center_angle, right_angle)

    
    
    #left_edge = bresenham(beam[0], beam[1])
    
    #right_edge = bresenham(beam[0], beam[3])
    
    num_x_pixels = int(np.ceil(beam[:,0].max() - beam[:,0].min()))
    num_y_pixels = int(np.ceil(beam[:,1].max() - beam[:,1].min()))

    sensor_reading = np.full((num_x_pixels,num_y_pixels), 0.5)

    angles = np.arange(-bw/2*rad2deg,bw/2*rad2deg,rad2deg*bw_res)+center_angle

    x_offset = int(np.abs(beam[:,0].min()))
    y_offset = int(np.abs(beam[:,1].min()))

    # shift origin coords if the beam extents are less than zero
    if  beam[:,0].min() < 0:
        beam_origin[0] = x_offset

    if beam[:,1].min() < 0:
        beam_origin[1] = y_offset

    for theta in angles:
        beam_extent = [range_cells_max*np.cos(theta)+x_offset, range_cells_max*np.sin(theta)+y_offset]
        edge = bresenham(beam_origin, beam_extent)
        # print(beam_origin, beam_extent)
        # shift bem pixel coords by center offset
        #edge[0][:] += x_offset
        #edge[1][:] += y_offset
        # remove any out of range pixels
        s = edge[0] >=num_x_pixels
        edge[0][s] = num_x_pixels-1
        s = edge[1] >=num_y_pixels
        edge[1][s] = num_y_pixels-1
        
        sensor_reading[tuple(edge)] = 0
        for ind in range(0,edge.shape[1]):
            if abs((edge[0,ind]-x_offset)**2+(edge[1,ind]-y_offset)**2 - range_cells**2) < range_cells*2:
                # pixels at
                sensor_reading[tuple(edge[:,ind])] = 1
            elif ((edge[0,ind]-x_offset)**2+(edge[1,ind]-y_offset)**2 - range_cells**2) >= (range_cells)*2:
                sensor_reading[tuple(edge[:,ind])] = 0.5

    return sensor_reading, beam_origin, hdg

def main():
    """main"""
    
    # range_bearing_sample(0, 30, 1.0, 0.1, 1.0, 0.01,)
    # range_bearing_sample(45, 30, 1.0, 0.1, 1.0, 0.01,)
    # range_bearing_sample(60, 60, 1.0, 0.1, 1.0, 0.01,)

    data={}
    center={}
    angle = {}
    data[0], center[0], angle[0]  = range_bearing_sample(335, 60, 0.1, 1.8, 2.55, 0.01)

    single_plot = True
    if single_plot:
        fig1, axs1 = plt.subplots(1)
        axs1.imshow((data[0].T), aspect='equal', origin='lower')
        axs1.plot(center[0][0],center[0][1],'+',color='red')
        axs1.set_title(f"c='{center[0]}'angle='{angle[0]}'")
        plt.show()    
    else:
        data[1], center[1], angle[1]  = range_bearing_sample(30, 30, 0.1, 0.5, 1.0, 0.01)
        data[2], center[2], angle[2]  = range_bearing_sample(60, 30, 0.1, 0.1, 1.0, 0.01)
        data[3], center[3], angle[3]  = range_bearing_sample(90, 30, 0.1, 0.5, 1.0, 0.01)
        data[4], center[4], angle[4]  = range_bearing_sample(120, 30, 0.1, 0.5, 1.0, 0.01)
        data[5], center[5], angle[5]  = range_bearing_sample(150, 30, 0.1, 0.5, 1.0, 0.01)
        data[6], center[6], angle[6]  = range_bearing_sample(180, 30, 0.1, 0.5, 1.0, 0.01)
        data[7], center[7], angle[7]  = range_bearing_sample(210, 30, 0.1, 0.5, 1.0, 0.01)
        data[8], center[8], angle[8]  = range_bearing_sample(240, 30, 0.1, 0.5, 1.0, 0.01)
        data[9], center[9], angle[9]  = range_bearing_sample(270, 30, 0.1, 0.5, 1.0, 0.01)
        data[10], center[10], angle[10] = range_bearing_sample(0, 30, 0.1, 0.5, 1.0, 0.01)
        data[11], center[11], angle[11]  = range_bearing_sample(0, 30, 0.1, 0.5, 1.0, 0.01)
        fig, axs= plt.subplots(4, 3)
        for i in range(0,4):
            for j in range(0,3):
                print(i*3+j)
                #axs[i,j].imshow(np.flipud(np.rot90(data[i*3+j])), aspect='equal', origin='lower')
                axs[i,j].imshow((data[i*3+j].T), aspect='equal', origin='lower')
                axs[i,j].plot(center[i*3+j][0],center[i*3+j][1],'+',color='red')
                axs[i,j].set_title(f"c='{center[i*3+j]}'angle='{angle[i*3+j]}'")
        # ax2.plot(x,data)
        plt.show()

if __name__ == "__main__":
    main()



#######################################


def range_bearing_reading(hdg, bw, bw_res, rng, rng_max, rng_res, ctr):
    """ 
    return an array representing the occupancy values of a range-bearing sensor
        bw = sensor effective beamwidth in degrees
        rng = range reading in meters
        bw_res = angular resolutioon in degress
        rng_res = range resolution in meters
    """ 
    rad2deg = np.pi/180
    print(np.pi)
    range_cells_max = floor(rng_max/rng_res)
    range_cell = floor(rng/rng_res)
    brg_cells = floor(bw/bw_res)
    center_angle = hdg*rad2deg
    left_angle = center_angle - (bw*rad2deg/2)
    if left_angle < 0:
        left_angle = left_angle + np.pi*2
    right_angle = center_angle + (bw*rad2deg/2)
    if right_angle < 0:
        right_angle = right_angle + np.pi*2
    reading = np.full((range_cells_max, 1),0.5)
    reading[0:range_cell-2] = 0.0
    reading[range_cell-2:range_cell+3] = np.array([[0.1], [0.3], [0.6], [0.9], [0.9] ])
    reading = np.tile(reading, [1, brg_cells])
    print(reading.shape)
    print(left_angle, right_angle)
    polar_image, convert_settings = polarTransform.convertToCartesianImage(reading.T,
                                                                          center=ctr,
                                                         #initialRadius=0,
                                                         #finalRadius=range_cells_max,
                                                         initialAngle=left_angle,
                                                         finalAngle=right_angle)
    print(convert_settings)   
    print(polar_image.shape)                                                  
    return polar_image, np.flipud(convert_settings.center)


    
def range_bearing_sample2(hdg, bw, bw_res, rng, rng_max, rng_res):
    """ return an array representing the occupancy values of a range-bearing sensor
        bw = sensor effective beamwidth in degrees
        rng = range reading in meters
        bw_res = angular resolutioon in degress
        rng_res = range resolution in meters
    """ 
    rad2deg = np.pi/180
    
    range_cells_max = floor(rng_max/rng_res)
    range_cells = floor(rng/rng_res)
    brg_cells = floor(bw/bw_res)
    center_angle = hdg*rad2deg
    left_angle = center_angle + (bw*rad2deg/2)
    # if left_angle < 0:
    #     left_angle = left_angle + np.pi*2
    right_angle = center_angle - (bw*rad2deg/2)
    # if right_angle < 0:
    #     right_angle = right_angle + np.pi*2

    left_beam_extent = [range_cells_max*np.cos(left_angle), range_cells_max*np.sin(left_angle)]
    center_beam_extent = [range_cells_max*np.cos(center_angle), range_cells_max*np.sin(center_angle)]
    right_beam_extent = [range_cells_max*np.cos(right_angle), range_cells_max*np.sin(right_angle)]
    beam_origin = [0, 0]
    beam = np.array([beam_origin, left_beam_extent, center_beam_extent, right_beam_extent])
    
  
    #beam=np.transpose(beam)
    print(beam)

    reading = np.full((range_cells_max, 1),0.5)
    reading[0:range_cells-2] = 0.0
    reading[range_cells-2:range_cells+3] = np.array([[0.1], [0.3], [0.6], [0.9], [0.9] ])

    #print(left_angle, center_angle, right_angle)
 
    #left_edge = bresenham(beam[0], beam[1])
    
    #right_edge = bresenham(beam[0], beam[3])
    
    num_x_pixels = int(np.ceil(left_beam_extent[0].max() - right_beam_extent[0].min()))
    num_y_pixels = int(np.ceil(left_beam_extent[1].max() - right_beam_extent[1].min()))

    sensor_reading = np.full((num_x_pixels+3,int(num_y_pixels/2)+1), 0.5)
    print(sensor_reading.shape)
    angles = np.arange(0,bw*rad2deg/2,rad2deg*bw_res)
    
    for theta in angles:
        beam_extent = [range_cells_max*np.cos(theta), range_cells_max*np.sin(theta)]
        edge = bresenham(beam_origin, beam_extent)
        s = edge[0] >=num_x_pixels
        edge[0][s] = num_x_pixels-1
        s = edge[1] >=num_y_pixels
        edge[1][s] = num_y_pixels-1
        sensor_reading[tuple(edge)] = 1
    
    mirror = np.fliplr(sensor_reading)
    sensor_reading = np.concatenate((mirror,sensor_reading), axis=1)


    sensor_reading = rotate(sensor_reading,hdg, reshape=True, order = 1, mode='constant', cval=0.5)

    # # plot the sensor pattern
    # fig, axs= plt.subplots(1)
    # #for idx in range(0,2):
    # axs.scatter(left_beam_extent[0],left_beam_extent[1])#,'.',color='red')
    # #axs.plot(beam_origin, left_beam_extent,color='red')
    # axs.plot(left_edge[0],left_edge[1],color='red')
    
    # axs.scatter(right_beam_extent[0],right_beam_extent[1],color='green')#,'.',color='green')
    # #axs.plot(beam_origin,right_beam_extent,'.k',color='green')
    # axs.plot(right_edge[0],right_edge[1],'.k',color='green')

    # axs.scatter(center_beam_extent[0],center_beam_extent[1])#,'.',color='blue')
    
    # axs.scatter(0,0)
    # axs.set_aspect(1)
    # axs.grid()
    # plt.show()
                                            
    return sensor_reading, beam_origin, hdg
