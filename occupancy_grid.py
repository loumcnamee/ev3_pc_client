#!/usr/bin/env python3
# experiemnts and tests with occupancy grids

import numpy as np
import matplotlib.pyplot as plt
from roboticstoolbox import DiffSteer, OccupancyGrid, RangeBearingSensor
from math import pi

class Occupancy_Map():
    
    def __init__(self, x_size, y_size, resolution=0.1):
        self.x_size = x_size
        self.y_size = y_size
        self.resolution = resolution
        self.grid_size = x_size * y_size
        self.log_odds_prob = np.zeros((int(self.x_size / resolution), int(self.y_size / resolution)),order='C')
        self.log_occupied = 0.84
        self.log_free = 0.4
 
    
    #def sensor_reading(self,pose,beamwidth,range):


    def visualize(self):
        print("The map \n" + str(self.log_odds_prob))
        #plt.scatter(self.curr_veh_pt[0], self.curr_veh_pt[1], s=20)
        #plt.imshow(self.log_odds_prob, interpolation ='none', cmap = 'binary')
        #plt.show()
    
    def update_log_odds(self, x, y, occupied = True):
        loc_present = [int(x/self.resolution),int(y/self.resolution)]
        x,y = loc_present
        if occupied == True:
            self.log_odds_prob[x, y] = self.log_odds_prob[x, y] + self.log_occupied
            if self.log_odds_prob[x, y] > 3.5:
                self.log_odds_prob[x, y] = 3.5
        else:
            self.log_odds_prob[x, y] = self.log_odds_prob[x, y] - self.log_free
            if self.log_odds_prob[x, y] < -2:
                self.log_odds_prob[x, y] = -2

if __name__ == "__main__":
    env_map = Occupancy_Map(100,100)
    env_map.visualize()

def main():
    """main"""
 
    robot = DiffSteer()
    map = OccupancyGrid(100)
    sensor = RangeBearingSensor(robot, map, range=(0.5, 20), angle=pi/4)
    print(sensor)
