#!/usr/bin/env python3
# experiemnts and tests with occupancy grids

from math import floor
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import NDArray
from scipy.ndimage import rotate
import occupancy_grid as og

#import DiffSteer, OccupancyGrid, RangeBearingSensor

# import time
# import keyboard 

def main():
    """main"""
    
    # range_bearing_sample(0, 30, 1.0, 0.1, 1.0, 0.01,)
    # range_bearing_sample(45, 30, 1.0, 0.1, 1.0, 0.01,)
    # range_bearing_sample(60, 60, 1.0, 0.1, 1.0, 0.01,)

    data={}
    center={}
    angle = {}
    map = og.Occupancy_Grid(5,5,0.01)
    data[0], center[0], angle[0]  = map.range_bearing_sample(30, 30, 0.1, 2.0, 2.55, 0.01)
    map.sensor_reading(250, 250, 45, 10, 0.1, 1.25, 2.55, 0.01)
    map.sensor_reading(250, 250, 65, 10, 0.1, 1.25, 2.55, 0.01)
   
    map.plot_grid()
    
    
    single_plot = True
    if single_plot:
        fig1, axs1 = plt.subplots(1)
        axs1.imshow((data[0].T), aspect='equal', origin='lower')
        axs1.plot(center[0][0],center[0][1],'+',color='red')
        axs1.set_title(f"c='{center[0]}'angle='{angle[0]}'")
        #plt.show()    
    else:
        data[1], center[1], angle[1]  = map.range_bearing_sample(30, 30, 0.1, 0.5, 1.0, 0.01)
        data[2], center[2], angle[2]  = map.range_bearing_sample(60, 30, 0.1, 0.1, 1.0, 0.01)
        data[3], center[3], angle[3]  = map.range_bearing_sample(90, 30, 0.1, 0.5, 1.0, 0.01)
        data[4], center[4], angle[4]  = map.range_bearing_sample(120, 30, 0.1, 0.5, 1.0, 0.01)
        data[5], center[5], angle[5]  = map.range_bearing_sample(150, 30, 0.1, 0.5, 1.0, 0.01)
        data[6], center[6], angle[6]  = map.range_bearing_sample(180, 30, 0.1, 0.5, 1.0, 0.01)
        data[7], center[7], angle[7]  = map.range_bearing_sample(210, 30, 0.1, 0.5, 1.0, 0.01)
        data[8], center[8], angle[8]  = map.range_bearing_sample(240, 30, 0.1, 0.5, 1.0, 0.01)
        data[9], center[9], angle[9]  = map.range_bearing_sample(270, 30, 0.1, 0.5, 1.0, 0.01)
        data[10], center[10], angle[10] = map.range_bearing_sample(0, 30, 0.1, 0.5, 1.0, 0.01)
        data[11], center[11], angle[11]  = map.range_bearing_sample(0, 30, 0.1, 0.5, 1.0, 0.01)
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


