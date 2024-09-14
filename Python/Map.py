import numpy as np
import grid_map as gm
import models_robot as mr
from matplotlib import pyplot as plt


ticks_vec = []
range_vec = []
pos_1 = [0,0,0]
dt = 0.5

def set_arrays(ticks, range):
    ticks_vec = ticks
    range_vec = range

def plot_map():

    #------ Map parameters ----#
    rows = 100
    cols = 100
    grid_size = 5
    bounds = {
        "EMPTY_CELL" : 0,
        "OBSTACLE_CELL" : 1,
        "START_CELL" : 2,
        "GOAL_CELL" : 3,
        "MOVE_CELL" : 4
    }
    new_map = gm.map(rows, cols)
    
    #----- Kinematic Models -----# 
    # ut -> Control is a set of two pose estimates obtained by the robot's odometer.
    # ut = (xb_t-1 xb_t), with:
    # xb_t-1 = (xb yb thetab)
    # xb_t = (xb' yb' thetab')
    
    # The controls are initialized. It supposed the vehicles begins at a position/pose [0,0,0].
    ut = list()
    ut.append([0.0, 0.0, 0.0])
    ut.append([0.0, 0.0, 0.0])
    
    for ticks in ticks_vec:
    
    # The list of samples is reset every calculation for each odometric control.
        samples_x = []
        samples_y = []
        samples_t = []
        samples = list()
    
    # It is estimated the vehicle movement in function of the odometric data gatered from the sensors.
    # the km list has the estimation for the position x, y and the orientation theta in radians.
    # The xt element of the control ut is updated in base of the kinematic estimation, accumulating the
    # movement from the previous value.
        
        km = mr.kinematic_model(ticks, dt, ut[0][2])
        ut[1] = [ut[1][0]+km[0], ut[1][1]+km[1], ut[1][2]+km[2]]
        print(ut)
        
    # It is sampled the estimation of position according to the odometric model taken from the book.
    # The control ut is a list formed by the previous position and the estimation calculated in the
    # previous lines from the kinematic model.
        
        for i in range(50):
            est = mr.odometry_motion_model(ut, pos_1)
            samples_x.append(est[0])
            samples_y.append(est[1])
            samples_t.append(est[2])
            samples.append([est[0], est[1], est[2]])
    
    # The functional position is chosen from a kmeans algorithm (by this version) among the estimated samples.
            
        centers = mr.kmeans_pos(samples, 1)
        pos_1 = centers[0]
        km = mr.kinematic_model(ticks, dt, ut[0][2])
    
    # Update of the last position from the actual position of this round.
        
        ut[0] = ut[1]
    
     #------ Map draw -------#   
        for g in range(len(samples_x)):
            # Get map grids position of each one of samples.
            grid_data = new_map.get_grid(samples_x[g], samples_y[g])
            # Verify the position in function of the current map.
            label = new_map.probability_position_map(grid_data[0], grid_data[1])
            # Update map.
            new_map.set_cell(grid_data, label)
    
            for s in range(1):
                sensor_data = mr.sample_range_sensor(samples_t[g]-(np.pi/2))
                #print(sensor_data)
                s_data = [sensor_data[0]+grid_data[0], sensor_data[1]+grid_data[1]]
                s_data = new_map.get_grid(s_data[0], s_data[1])
                new_map.set_cell(s_data, bounds["MOVE_CELL"])
     
        plt.plot(samples_x, samples_y, 'o')
        plt.plot(centers[0][0], centers[0][1], "ko")
        plt.xlabel("x")
        plt.ylabel("y")
    
    plt.plot(0, 0, 'ko',)
    new_map.plot_grid()
    plt.show()
