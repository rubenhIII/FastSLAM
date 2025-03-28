from threading import Thread
from multiprocessing import Process, Value, Array, Manager
from ctypes import Structure, c_double, c_int, c_float
import copy

import threading as threading
import numpy as np
import logging
import random
import time

# From test_models.py
# ------------------------
import numpy as np
import grid_map as gm
import models_robot as mr
# -------------------------

class cell_occuped:
    def __init__(self, x, y, p, l) -> None:
        self.x = x
        self.y = y
        self.p = 0
        self.l = 0
    
class grid_occuped():
    def __init__(self) -> None:
        self.cells = []

    def append(self, x, y, p, l):
        cell = cell_occuped(x, y, p, l)
        self.cells.append(cell)
        return cell
    
    def find(self, x, y):
        if len(self.cells) != 0:
            for cell in self.cells:
                if cell.x == x and cell.y == y:
                    return cell
        return False
    
    def update_cell(self, x, y, p, l):
        if len(self.cells) != 0:
            for cell in self.cells:
                if cell.x == x and cell.y == y:
                    cell.p = p
                    cell.l = l

def trunc_cell(x, y):
        grid_x = int(np.trunc(x))
        grid_y = int(np.trunc(y))
        return [grid_x, grid_y]


# ----- Code test models begins ----------

ticks_vec = [
[3.0,5.0,6.0,1.0,],
[2.0,5.0,4.0,1.0,],
[4.0,3.0,4.0,0.0,],
[5.0,6.0,4.0,0.0,],
[5.0,4.0,5.0,2.0,],
[4.0,5.0,3.0,3.0,],
[2.0,4.0,3.0,3.0,],
[4.0,4.0,6.0,4.0,],
[5.0,2.0,6.0,3.0,],
[2.0,6.0,5.0,3.0,],
[3.0,4.0,5.0,2.0,],
[4.0,4.0,4.0,4.0,],
[5.0,4.0,5.0,2.0,],
[2.0,4.0,5.0,3.0,],
[2.0,5.0,2.0,0.0,],
[4.0,4.0,5.0,3.0,],
[4.0,4.0,6.0,2.0,],
[6.0,4.0,5.0,3.0,],
[3.0,5.0,5.0,2.0,],
[5.0,5.0,2.0,2.0,],
[6.0,4.0,6.0,4.0,],
[3.0,6.0,5.0,2.0,],
[3.0,5.0,6.0,2.0,],
[3.0,5.0,2.0,1.0,],
[5.0,3.0,4.0,3.0,],
[3.0,6.0,5.0,1.0,]
]

range_vec = [
[63.59,62.99,63.71,64.84,101.39,96.23,98.65,215.16,213.77,212.37,0.0,89.56,126.81,129.04,127.6,64.72,61.41,59.87,59.12,59.27,61.12,60.3,],
[64.0,64.19,65.36,446.36,3175.48,71.65,283.34,280.99,215.11,194.82,0.0,90.53,128.8,127.68,129.74,64.52,61.95,60.45,59.18,59.3,58.82,59.61,],
[49.75,50.3,51.42,83.16,81.27,81.7,252.52,274.18,201.75,0.29,187.76,187.42,199.99,369.58,135.78,3162.56,61.07,61.07,59.34,58.7,59.29,59.41,],
[49.98,50.99,51.64,76.83,76.54,79.88,267.37,265.65,199.52,0.0,192.42,190.23,190.38,118.56,116.28,75.39,62.53,61.24,60.02,59.72,59.68,60.37,],
[50.52,50.99,52.08,72.89,73.66,237.05,258.69,259.19,182.94,0.0,175.68,173.2,121.4,110.82,75.36,75.0,61.93,59.77,59.77,59.03,59.32,59.03,],
[50.85,50.99,52.05,3164.74,66.46,261.25,252.04,175.29,175.67,172.85,174.14,173.63,172.92,179.56,3154.0,59.87,60.28,59.05,58.31,58.0,58.69,58.55,],
[50.63,51.19,51.83,178.91,211.8,227.68,224.75,168.82,166.61,0.0,156.43,158.05,157.18,252.53,254.3,72.97,60.09,59.3,58.5,58.02,58.21,58.16,],
[51.66,51.84,52.5,174.86,215.1,213.79,189.99,160.68,158.88,147.76,146.68,147.8,159.44,245.45,64.86,61.77,59.87,58.57,57.8,57.32,57.52,57.9,],
[51.95,52.55,52.79,175.29,205.23,207.24,208.17,152.34,151.69,0.0,140.94,140.97,139.16,239.59,75.32,72.94,70.35,60.92,59.0,58.02,58.94,59.39,],
[52.79,53.68,175.87,193.74,202.18,223.98,174.4,146.72,144.42,0.12,131.71,132.67,132.88,137.29,232.81,59.75,57.68,56.47,56.01,56.35,56.89,57.32,],
[51.19,51.74,53.25,190.62,198.39,213.65,141.49,138.4,125.78,130.31,124.42,127.17,124.35,123.86,229.4,59.22,57.54,55.36,55.72,55.33,55.69,56.08,],
[51.54,52.12,53.63,186.04,191.6,191.7,192.49,131.27,120.07,0.05,117.89,119.57,119.0,116.4,128.69,59.41,56.15,55.57,55.31,55.07,55.57,55.02,],
[52.22,53.17,53.83,182.75,192.42,185.13,180.06,126.38,125.98,113.43,112.18,111.03,110.93,115.04,124.2,68.7,56.65,56.18,55.12,55.69,54.71,55.46,],
[51.93,52.5,54.01,185.58,178.24,175.08,121.71,117.67,118.88,0.0,107.22,110.79,106.83,107.0,121.32,59.54,58.09,57.4,56.27,55.87,56.7,56.2,],
[52.39,52.89,53.54,171.74,169.01,167.54,114.78,107.36,106.84,107.63,106.06,104.32,106.78,109.31,124.41,122.67,60.37,57.14,56.32,55.84,55.75,55.82,],
[52.05,52.34,53.46,179.78,161.66,161.54,174.57,107.55,101.43,0.0,91.6,95.23,95.8,103.98,107.41,96.9,96.93,95.63,95.23,59.0,58.1,58.43,],
[52.56,0.26,53.17,53.11,55.03,155.82,155.38,75.25,93.14,0.0,0.0,0.17,86.09,93.12,189.37,189.42,99.08,96.55,97.17,94.81,95.32,96.81,],
[53.11,53.65,56.01,99.21,100.6,147.46,146.87,88.7,85.06,83.61,84.72,85.0,79.56,80.73,104.12,178.5,211.53,99.85,97.38,97.34,65.26,64.18,],
[54.57,55.15,99.38,99.9,143.34,145.21,112.44,111.49,107.44,0.29,69.77,91.82,77.59,77.43,116.28,121.89,151.54,99.93,97.98,98.08,65.32,65.98,],
[55.38,55.81,99.28,100.02,136.12,137.05,136.17,102.78,73.16,71.16,71.22,73.54,72.51,68.79,71.81,162.2,204.65,102.09,100.14,99.68,70.16,70.23,],
[58.19,97.79,98.42,131.27,132.04,130.2,130.96,96.55,65.2,0.0,62.75,62.22,61.86,61.21,67.76,99.02,110.21,108.42,102.75,102.61,74.53,74.29,],
[89.49,102.75,127.3,126.45,127.05,124.8,125.52,126.5,60.21,0.0,55.93,55.86,55.63,60.08,66.08,139.89,135.73,112.3,106.18,104.99,103.16,105.1,],
[98.13,100.07,121.94,122.23,119.84,121.8,124.65,124.47,81.0,0.0,50.11,50.06,48.96,50.83,56.32,63.08,142.91,143.46,109.85,110.1,107.31,107.53,],
[86.69,101.97,117.8,115.37,114.99,114.84,114.58,116.29,115.01,0.12,42.84,77.24,62.24,56.92,57.13,135.38,134.11,135.24,135.09,112.59,112.57,111.1,],
[101.72,114.17,110.46,110.48,111.1,111.72,110.26,109.43,65.87,0.12,60.35,64.04,63.44,63.75,52.92,52.99,164.11,163.3,257.99,118.7,116.0,117.25,],
[111.34,108.37,106.42,105.9,107.29,103.81,103.24,102.57,59.92,0.14,29.69,55.72,57.2,56.65,67.35,100.6,162.36,161.31,161.74,157.13,119.26,121.51,]
]

# -------------------------

def slam(g, tick_index, samples_x, samples_y, samples_t, samples_p, ut, occupancy_grids):
    #dt = 0.5
    #dt = 0.1875 # Para 3/16
    #dt = 0.126 # Para 2/16
    #dt = 0.0625 # Para 1/16
    dt = 0.125
    grid = copy.deepcopy(occupancy_grids[g])

    ticks_fixed = mr.fix_ticks(ticks_vec[tick_index])
    logging.info(f'{ticks_fixed}')
    km = mr.kinematic_model(ticks_fixed, dt, ut[g][0][2])
    ut_g1 = [ut[g][1][0]+km[0], ut[g][1][1]+km[1], ut[g][1][2]+km[2]]
    ut_g0 = ut[g][0]
    ut[g] = [ut_g0, ut_g1]
    
    pos_1 = [samples_x[g], samples_y[g], samples_t[g]]
    est = mr.odometry_motion_model(ut[g], pos_1)

    sample_x = est[0]
    sample_y = est[1]
    sample_t = est[2]
    sample_p = 0

    samples_x[g] = sample_x
    samples_y[g] = sample_y
    samples_t[g] = sample_t

    

 #------ MCL Model -------#

    # -----------------------------------
    # -- Block of occupancy map update---
    # -----------------------------------
    particle_grid = trunc_cell(sample_x, sample_y)
    #grid_particle_pos = grid.append(particle_grid[0], particle_grid[1], 0, 0)
    #mcl_matrix[(int(XLEN/2)+particle_grid[0])%500, (particle_grid[1]+int(YLEN/2))%500] = 0.5
    file_name_trajectory = "./results/trajectory.txt"
    myFile = open(file_name_trajectory, 'a', encoding="utf-8")
    myFile.write(f'c({(int(XLEN/2) + particle_grid[0])%XLEN},{(particle_grid[1]+int(YLEN/2))%YLEN}),\n')
    myFile.close()
    # -------------------------------
    # End of block occupancy update
    # -------------------------------

    servo_error = 0
    range_distances = range_vec[tick_index]
    range_pos = -90 + servo_error
    range_angles = list(range(-90 + servo_error, 108 + servo_error, 9))
    range_angles = [x * np.pi/180.0 for x in range_angles]
    angles_counter = 0
    q = 1

    for s in range_distances:
        if s <= 100:
            #s = 150
            z_t = range_pos * np.pi / 180.0
            # The third argument (x and y) correspond to the sensor position in respect to the vehicle center.
            sensor_data = mr.likelihood_field_range_finder_model([s], [sample_x, sample_y, sample_t], [0, 0, z_t])
  
            s_data = [sensor_data[0], sensor_data[1]]
            s_data = trunc_cell(s_data[0], s_data[1])
            #mcl_matrix[int(XLEN/2)+s_data[0], s_data[1]+int(YLEN/2)] = 1

            # Likelihood calculation
            dist = mr.nearest_neighbour(grid, s_data[0], s_data[1])
            q = q * mr.likelihood_field_range_finder_prob(dist)
               
            # -----------------------------------
            # -- Block of occupancy map update---
            # -----------------------------------
            # Grids in the beam path!
            #'''
            angle_range = list(np.arange(-7, 8, 1))
            angle_step = [x * np.pi / 180 for x in angle_range]
            distance_step = 0.5
            distance_range = list(np.arange(1, s + 0, distance_step))
            distance_range.append(s)
                
            for angle in angle_step:
                for distance in distance_range:
                    sensor_data_beam = mr.likelihood_field_range_finder_model(
                            [distance], [sample_x, sample_y, sample_t], 
                            [0, 0, z_t + angle])
                    s_data_beam = [sensor_data_beam[0], sensor_data_beam[1]]
                    s_data_beam = trunc_cell(s_data_beam[0], s_data_beam[1])
                        
                    grid_beam_pos = grid.find(s_data_beam[0],s_data_beam[1])
                    if grid_beam_pos == False:
                        grid_beam_pos = grid.append(s_data_beam[0],s_data_beam[1], 0.5, 0)

                    #logging.info(f'vec: {range_angles}')    
                    beam_probs = mr.occupancy_grid_mapping(grid_beam_pos.l, [particle_grid[0], particle_grid[1], sample_t], 
                                                           [range_distances, range_angles], [grid_beam_pos.x, grid_beam_pos.y])
                        
                    #mcl_matrix[int(XLEN/2)+s_data_beam[0], s_data_beam[1]+int(YLEN/2)] = 0.5
                    grid_beam_pos.l = beam_probs[0]
                    grid_beam_pos.p = beam_probs[1]
                
        range_pos = range_pos + 9
            #mcl_matrix[int(XLEN/2)+s_data[0], s_data[1]+int(YLEN/2)] = 0

    samples_p[g] = q
    sample_p = q
    #logging.info(f'Exit {occupancy_grids[g].cells}')
        # Update of the last position from the actual position for this particle.
    ut[g][0] = ut[g][1]
    ut[g] = [ut_g1, ut_g1]
    occupancy_grids[g] = grid

if __name__ == "__main__":

    # ---- Initialization ----
    # Sampling initial particles
    XLEN = 1000
    YLEN = 1000
    TLEN = 0
    SAMPLES = 1

    SAMPLE_BOUNDX = np.trunc((XLEN-1)/10)
    SAMPLE_BOUNDY = np.trunc((XLEN-1)/10)

    # Samples to be used in MCL model. Particles.
    manager = Manager()
    
    samples_x = manager.list()
    samples_y = manager.list()
    samples_t = manager.list()
    samples_p = manager.list()

    ut = manager.list()
    occupancy_grids = manager.list()

    # samples_x, samples_y, samples_t, samples_p, ut, occupancy_grids
             
   
    # ----------------------------------------

    logging.basicConfig(level=logging.INFO)
    random.seed(time.time())
    map_positions = np.zeros(XLEN * YLEN).reshape(XLEN, YLEN)
    mcl_matrix = (np.zeros(XLEN * YLEN).reshape(XLEN, YLEN)) + 0.5

    for i in range(SAMPLES):
        x_sample = random.randint(-SAMPLE_BOUNDX, SAMPLE_BOUNDX)
        y_sample = random.randint(-SAMPLE_BOUNDY, SAMPLE_BOUNDY)
        t_sample = random.uniform(0, TLEN)
        logging.info(f'Sample x: {x_sample} y: {y_sample} t: {t_sample}')
    
        map_positions[x_sample, y_sample] = 1
        samples_x.append(x_sample)
        samples_y.append(y_sample)
        samples_t.append(t_sample)
        samples_p.append(0.5)

        ut.append([[0,0,0],[0,0,0]])
        occupancy_grids.append(grid_occuped())

    pos_1 = [0,0,0]
    
    # ------------------------
    
    tick_index = 0
    POOL_SIZE = 4
    g = 0

    g_val = Value('i', g)
    tick_val = Value('i', tick_index)
    
    old_time = time.time()

    for ticks in ticks_vec:
        new_time = time.time()
        logging.info(f'Running on ticks {ticks} ... {tick_index / len(ticks_vec) * 100:.2f}% Time elapsed {(new_time - old_time) / 60:.2f} min.')
        g = 0
        while g < SAMPLES:
            thread_pool = []
            for t in range(POOL_SIZE):
                if g < SAMPLES:
                    #thread = Thread(target=slam, args=(g, tick_index, ), name="Thread " + str(t))
                    #logging.info(f'Before {occupancy_grids[g].cells}')
                    thread = Process(target=slam, args=(g, tick_index, samples_x, samples_y, samples_t, samples_p, ut, occupancy_grids, ),
                                      name="Process " + str(t))
                    thread_pool.append(thread)
                    thread.start()
                    logging.info(f'Running sample {g} in {thread.name} ...')
                    g = g + 1                  
                else:
                    break
            logging.info("Waiting for threads ...")
            for thread in thread_pool:
                if thread.is_alive():
                    thread.join()
                    
                   
        tick_index = tick_index + 1
    
        #'''
        # ---> Add re-sampling function
        logging.info("Re-sampling ...")
        Xt = list(range(SAMPLES))
        index_resample = mr.low_variance_sampler(Xt, samples_p)
        resamples_x = []
        resamples_y = []
        resamples_t = []
        resamples_p = []
        
        resamples_ut = []
        resamples_occupancy_grids = []
        
        for i in range(SAMPLES):
            resamples_x.append(samples_x[index_resample[i]])
            resamples_y.append(samples_y[index_resample[i]])
            resamples_t.append(samples_t[index_resample[i]])
            resamples_p.append(samples_p[index_resample[i]])
            
            resamples_ut.append([ut[index_resample[i]][0], ut[index_resample[i]][1]])
            resamples_occupancy_grids.append(occupancy_grids[index_resample[i]])
        
        samples_x = manager.list(resamples_x)
        
        samples_y = manager.list(resamples_y)
        samples_t = manager.list(resamples_t)
        samples_p = manager.list(resamples_p)
    
        ut = manager.list(resamples_ut)
        occupancy_grids = manager.list(resamples_occupancy_grids)
    
        # End re-sampling
        #'''

    logging.info("Saving results ...")    
    for cell in occupancy_grids[0].cells:
        mcl_matrix[(int(XLEN/2)+cell.x)%XLEN, (cell.y+int(YLEN/2))%YLEN] = cell.p
    
    file_name = "./results/mcl_map.txt"
    file_conn = open(file_name, 'w', encoding="utf-8")
    for x in range(XLEN):
        for y in range(YLEN):
            if file_conn != None:
                file_conn.write(f'{mcl_matrix[x,y]} ')
        file_conn.write("\n")
    file_conn.close()