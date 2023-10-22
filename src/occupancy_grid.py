#!/usr/bin/env python3
# experiemnts and tests with occupancy grids

import numpy as np
import matplotlib.pyplot as plt
from math import pi
from math import floor

    # copied from https://github.com/bdaiinstitute/spatialmath-python/blob/07c6f62460030fd2c4f45112611e783abfbd8e4f/spatialmath/base/numeric.py#L229
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



class Occupancy_Grid():
    
    def __init__(self, x_size, y_size, resolution=0.1):
        self.x_size = x_size
        self.y_size = y_size
        self.resolution = resolution
        self.grid_size = x_size * y_size
        self.log_odds_prob = np.full((int(self.x_size / resolution), int(self.y_size / resolution)), 0.5,order='C')
        #np.zeros((int(self.x_size / resolution), int(self.y_size / resolution)),order='C')
        self.log_occupied = 0.84
        self.log_free = 0.4
 
    
    #def sensor_reading(self,pose,beamwidth,range):
    def get_map(self):
        return self.log_odds_prob

    def visualize(self):
        print("The map \n" + str(self.log_odds_prob))
        #plt.scatter(self.curr_veh_pt[0], self.curr_veh_pt[1], s=20)
        #plt.imshow(self.log_odds_prob, interpolation ='none', cmap = 'binary')
        #plt.show()
    
    def update_log_odds(self, x, y, value):
        loc_present = [int(x),int(y)]
        #print(loc_present)
        #[int(x/self.resolution),int(y/self.resolution)]
        x,y = loc_present
        if value != 0.5:
            self.log_odds_prob[x,y]  = self.log_odds_prob[x, y] + value
        
        if value == 0:
            self.log_odds_prob[x,y]  = self.log_odds_prob[x, y]/2
        # if value >= self.log_occupied:
        #     self.log_odds_prob[x, y] = self.log_odds_prob[x, y] + self.log_occupied
        #     if self.log_odds_prob[x, y] > 3.5:
        #         self.log_odds_prob[x, y] = 3.5
        # else:
        #     self.log_odds_prob[x, y] = self.log_odds_prob[x, y] - self.log_free
        #     if self.log_odds_prob[x, y] < -2:
        #         self.log_odds_prob[x, y] = -2

    def update_grid(self, data, x, y, x_offset=0, y_offset=0):
        print(x,y,x_offset, y_offset)
        it = np.nditer(data, flags=['multi_index'])
        for cell in it:
            self.update_log_odds(x-x_offset+it.multi_index[0], y-y_offset+it.multi_index[1], cell)

    def sensor_reading(self, x, y, hdg, bw, bw_res, rng, rng_max, rng_res ):
        data, center, angle  = self.range_bearing_sample(hdg, bw, bw_res, rng, rng_max, rng_res )
        self.update_grid(data, x, y, center[0], center[1])

    def plot_grid(self):
        plt.imshow(self.log_odds_prob.T, aspect='equal', origin='lower', cmap='hot')
        plt.show()
    

    def range_bearing_sample(self, hdg, bw, bw_res, rng, rng_max, rng_res):
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
            band = range_cells-36
            for ind in range(0,edge.shape[1]):
                cell = (edge[0,ind]-x_offset)**2+(edge[1,ind]-y_offset)**2 - (range_cells**2)
                if abs(cell) <= (range_cells*2):
                    # pixels at range have occupancy likelihood of 1
                    sensor_reading[tuple(edge[:,ind])] = 1.0
                elif cell >= (range_cells)*2:
                    sensor_reading[tuple(edge[:,ind])] = 0.5
                elif (abs(cell) <= ((range_cells-band)**2)) : #and (abs(cell) > ((range_cells)**2))
                    sensor_reading[tuple(edge[:,ind])] = 0.75

        return sensor_reading, beam_origin, hdg
