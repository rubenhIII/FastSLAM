import numpy as np
import random
import time

# From test_models.py
# ------------------------
import numpy as np
import grid_map as gm
import models_robot as mr
from matplotlib import pyplot as plt
# -------------------------

class cell_occuped:
    def __init__(self, x, y, p, l) -> None:
        self.x = x
        self.y = y
        self.p = 0
        self.l = 0
    
class grid_occuped:
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

# Sampling initial particles

XLEN = 500
YLEN = 500
TLEN = 0
SAMPLES = 30

SAMPLE_BOUNDX = np.trunc((XLEN-1)/100)
SAMPLE_BOUNDY = np.trunc((XLEN-1)/100)

# Samples to be used in MCL model. Particles.
samples_x = []
samples_y = []
samples_t = []
samples_p = []

ut = []
occupancy_grids = []

random.seed(time.time())
map_positions = np.zeros(XLEN * YLEN).reshape(XLEN, YLEN)
mcl_matrix = np.zeros(XLEN * YLEN).reshape(XLEN, YLEN)

#print("Sampling")
for i in range(SAMPLES):
    x_sample = random.randint(-SAMPLE_BOUNDX, SAMPLE_BOUNDX)
    y_sample = random.randint(-SAMPLE_BOUNDY, SAMPLE_BOUNDY)
    t_sample = random.uniform(0, TLEN)

    map_positions[x_sample, y_sample] = 1
    samples_x.append(x_sample)
    samples_y.append(y_sample)
    samples_t.append(t_sample)
    samples_p.append(0.5)

    ut.append([[0,0,0,0],[0,0,0,0]])
    occupancy_grids.append(grid_occuped())

#    print(f'X:{x_sample} Y:{y_sample} T:{t_sample}')



# ----- Code test models begins ----------
ticks_vec = [
[1.0,1.0,2.0,2.0,],
[2.0,0.0,2.0,2.0,],
[1.0,0.0,2.0,1.0,],
[2.0,0.0,2.0,1.0,],
[2.0,1.0,1.0,1.0,],
[2.0,0.0,2.0,2.0,],
[2.0,2.0,2.0,0.0,],
[1.0,1.0,2.0,2.0,],
[2.0,1.0,1.0,1.0,],
[2.0,1.0,2.0,0.0,],
[1.0,2.0,2.0,1.0,],
[2.0,0.0,2.0,0.0,],
[2.0,1.0,1.0,1.0,],
[1.0,2.0,2.0,2.0,],
[1.0,2.0,2.0,2.0,],
[2.0,2.0,2.0,1.0,],
[2.0,1.0,2.0,1.0,],
[2.0,1.0,1.0,1.0,],
[2.0,2.0,2.0,1.0,],
[2.0,2.0,2.0,2.0,],
[1.0,2.0,2.0,1.0,],
[1.0,1.0,2.0,1.0,],
[1.0,1.0,1.0,2.0,],
[2.0,1.0,2.0,0.0,],
[1.0,1.0,2.0,2.0,],
[1.0,0.0,2.0,2.0,],
[1.0,1.0,1.0,2.0,],
[2.0,2.0,2.0,1.0,],
[1.0,0.0,2.0,1.0,],
[2.0,2.0,2.0,1.0,],
[0.0,2.0,2.0,1.0,],
[1.0,1.0,2.0,2.0,],
[2.0,0.0,2.0,2.0,],
[2.0,1.0,2.0,0.0,]
]

range_vec = [
[20.34,22.66,74.4,86.2,66.71,64.84,64.67,64.4,64.55,64.88,65.51,37.37,35.88,37.68,27.73,26.24,25.86,25.02,24.87,25.54,26.94,26.94,],
[20.32,25.07,73.3,94.19,64.84,63.37,63.21,62.97,62.77,62.68,39.99,36.74,35.55,33.65,29.17,27.15,25.52,24.35,25.33,26.03,26.19,26.19,],
[20.19,22.05,93.31,68.27,63.66,61.81,61.65,61.19,61.0,61.36,62.01,35.93,33.05,33.2,28.86,26.93,25.74,25.0,25.02,27.85,27.39,27.41,],
[19.53,21.28,72.48,91.08,62.0,60.13,59.87,59.65,59.37,59.49,59.9,38.36,34.16,32.19,30.61,27.2,26.0,25.81,25.5,26.03,56.66,57.52,],
[19.52,20.99,73.74,65.36,60.68,59.39,58.6,58.7,57.3,58.26,58.43,36.75,32.6,31.61,32.64,27.77,26.55,25.69,25.42,25.72,28.11,27.58,],
[19.47,21.04,74.55,87.34,59.41,57.5,57.23,57.38,55.94,56.59,57.18,59.72,94.07,32.98,28.83,27.22,26.0,25.43,25.48,25.57,27.15,27.25,],
[19.59,21.04,88.94,77.71,58.53,56.22,56.06,55.74,55.17,56.13,56.03,61.74,63.73,76.49,32.12,26.91,26.12,25.67,25.43,25.69,27.34,27.58,],
[19.57,21.04,87.1,75.85,57.8,55.17,54.59,54.28,53.7,54.26,54.54,62.17,62.34,31.4,28.52,27.37,26.14,24.97,25.52,25.76,27.17,27.15,],
[19.62,20.97,78.89,75.97,56.01,53.3,53.17,52.84,52.38,52.79,53.53,55.1,60.78,62.72,28.42,26.86,26.05,25.48,25.55,25.62,27.18,27.29,],
[19.53,20.94,85.36,75.82,54.52,51.5,51.71,50.99,50.56,50.99,51.28,52.99,34.08,31.76,32.74,27.51,26.31,25.45,25.57,25.55,28.28,27.75,],
[19.52,20.43,74.45,71.88,52.38,51.24,49.94,49.58,49.03,49.58,49.98,51.57,58.41,31.66,28.45,27.46,26.65,25.93,25.72,26.05,27.37,28.23,],
[19.77,20.37,71.77,54.37,50.52,49.36,48.55,47.83,47.59,48.23,48.11,52.96,56.84,30.65,29.4,73.54,26.81,26.15,25.86,25.97,28.35,28.43,],
[19.28,20.63,73.92,54.74,50.46,47.54,46.32,46.13,45.88,46.08,46.7,56.39,54.14,86.5,28.5,27.66,26.86,26.19,25.52,26.07,28.85,28.85,],
[19.12,20.15,69.32,72.12,46.94,46.1,44.47,44.13,44.02,44.2,44.81,46.84,65.12,67.79,70.31,27.54,26.21,25.48,26.14,26.0,27.75,27.75,],
[19.02,20.03,82.9,81.03,45.62,43.24,42.43,42.09,42.14,42.48,43.6,50.15,67.95,65.98,97.75,27.18,25.45,24.39,24.97,25.59,26.99,27.01,],
[18.86,19.93,80.76,81.43,45.14,41.9,41.3,40.68,40.32,41.06,42.19,50.78,52.99,65.79,75.05,26.36,25.55,24.95,25.48,25.66,26.69,26.79,],
[19.33,19.84,81.0,82.03,43.8,40.89,40.06,39.75,39.08,39.29,39.99,50.47,50.25,81.86,86.08,118.4,28.93,25.24,24.66,25.16,75.82,75.34,],
[18.78,19.83,78.72,79.7,98.41,39.65,38.19,38.0,36.7,37.54,38.66,48.35,49.82,82.22,78.36,26.24,25.45,24.87,25.76,26.21,28.52,28.52,],
[18.73,19.79,77.96,65.43,40.83,37.85,36.24,35.89,35.71,35.48,35.53,76.23,75.36,77.71,119.0,27.1,25.5,24.92,24.99,25.09,25.91,26.31,],
[18.64,19.24,76.11,76.42,38.88,35.55,34.28,33.94,33.75,33.94,33.99,38.62,73.54,77.54,36.0,28.52,26.91,25.71,25.12,25.33,25.86,25.54,],
[18.33,19.4,73.71,74.84,216.28,33.7,32.19,32.14,31.88,32.05,32.88,71.72,73.26,80.79,31.2,28.55,27.53,27.22,26.96,26.45,27.1,26.99,],
[18.26,18.88,74.04,77.96,194.26,32.1,30.1,30.08,29.82,30.05,31.18,70.44,79.64,72.63,72.03,28.14,27.66,26.5,26.31,26.05,27.13,27.46,],
[17.97,18.99,102.8,218.3,35.05,30.01,28.04,28.14,27.89,28.09,28.66,67.85,69.68,77.26,69.47,28.54,27.65,27.18,26.5,27.1,28.31,28.73,],
[17.72,18.32,99.86,191.29,191.02,27.99,26.84,26.07,26.15,26.38,27.15,66.99,67.18,78.62,75.37,29.41,27.41,27.41,27.22,27.41,27.99,27.68,],
[17.63,18.68,110.99,189.11,187.52,26.63,24.95,24.32,24.04,24.16,25.38,65.34,47.32,45.31,42.98,28.73,27.83,27.59,27.3,27.78,74.12,37.44,],
[17.53,18.99,113.65,242.16,189.54,24.56,23.39,23.1,22.33,22.62,23.2,63.92,64.95,65.0,74.43,29.1,27.56,27.54,27.34,27.54,28.66,27.82,],
[17.32,18.37,159.32,184.09,241.82,22.86,21.75,21.49,20.77,21.49,21.3,62.67,62.53,62.6,72.32,28.83,27.85,27.83,27.51,27.59,35.59,35.48,],
[17.22,18.68,114.27,203.57,47.59,21.88,19.88,19.36,19.21,19.41,20.53,61.07,61.55,62.68,64.62,29.34,28.09,27.05,27.51,27.77,28.88,28.88,],
[17.08,18.83,159.15,161.9,233.05,19.14,17.94,17.17,16.93,17.13,17.78,58.55,59.24,36.5,33.68,29.22,28.74,27.68,27.8,27.94,28.55,28.54,],
[19.04,110.6,158.72,248.93,299.54,17.22,15.98,15.66,15.42,15.16,15.83,58.77,57.57,37.25,36.44,29.76,28.57,28.21,27.85,28.01,29.14,28.71,],
[159.37,112.08,158.88,226.93,190.81,15.68,14.01,13.24,12.98,13.21,13.86,55.89,56.15,56.78,31.49,29.52,28.76,27.7,28.13,28.21,28.88,29.33,],
[112.35,152.41,155.04,195.53,194.84,13.5,11.83,11.54,11.27,11.32,11.63,53.99,54.33,54.98,33.53,30.68,29.02,28.26,28.26,27.75,29.58,29.58,],
[107.58,108.95,153.17,178.05,135.14,11.39,10.22,9.5,9.16,9.3,9.67,12.09,53.23,53.89,32.45,29.7,29.21,28.86,28.23,28.71,29.41,29.41,],
[106.38,107.34,158.38,172.72,124.7,9.24,7.94,7.27,7.48,7.12,7.92,10.7,51.06,52.05,32.57,30.22,29.33,28.55,28.37,28.54,28.91,29.24,],
]

pos_1 = [0,0,0]
dt = 0.5

# -------------------------

tick_index = 0
for ticks in ticks_vec:
    for g in range(SAMPLES):

        grid = occupancy_grids[g]

        km = mr.kinematic_model(ticks, dt, ut[g][0][2])
        ut[g][1] = [ut[g][1][0]+km[0], ut[g][1][1]+km[1], ut[g][1][2]+km[2]]

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
        mcl_matrix[int(XLEN/2)+particle_grid[0], particle_grid[1]+int(YLEN/2)] = 0.25
        # -------------------------------
        # End of block occupancy update
        # -------------------------------

        range_distances = range_vec[tick_index]
        range_pos = -90
        #range_angles = list(range(-90, 108, 9))
        range_angles = list(range(0, 198, 9))
        range_angles = [x * np.pi/180.0 for x in range_angles]
        angles_counter = 0
        q = 1

        for s in range_distances:
            if s <= 100:
                #s = 150
                z_t = range_pos * np.pi / 180.0
                # The third argument (x and y) correspond to the sensor position in respect to the vehicle center.
                sensor_data = mr.likelihood_field_range_finder_model([s], [sample_x, sample_y, sample_t], [1, 1, z_t])
  
                s_data = [sensor_data[0], sensor_data[1]]
                s_data = trunc_cell(s_data[0], s_data[1])

                # Likelihood calculation
                dist = mr.nearest_neighbour(grid, s_data[0], s_data[1])
                q = q * mr.likelihood_field_range_finder_prob(dist)
               
                # -----------------------------------
                # -- Block of occupancy map update---
                # -----------------------------------
                # Left to take into account all the grids in the beam path!

                grid_beam_pos = grid.find(s_data[0],s_data[1])
                if grid_beam_pos == False:
                    grid_beam_pos = grid.append(s_data[0],s_data[1], 0.25, np.log(0.25/0.75))
                beam_probs = mr.occupancy_grid_mapping(grid_beam_pos.l, [particle_grid[0], particle_grid[1], sample_t], 
                                                       [range_distances, range_angles], [grid_beam_pos.x, grid_beam_pos.y])
                grid_beam_pos.l = beam_probs[0]
                grid_beam_pos.p = beam_probs[1]

                # -------------------------------
                # End of block occupancy update
                # -------------------------------
                
            range_pos = range_pos + 9

        samples_p[g] = q
        sample_p = q

        # Update of the last position from the actual position for this particle.
        ut[g][0] = ut[g][1]
        print(f'x: {round(sample_x,2)} y: {round(sample_y,2)} t: {round(sample_t,2)} p: {round(sample_p,2)}') 
   
    tick_index = tick_index + 1

    #'''
    # ---> Add re-sampling function
    Xt = list(range(SAMPLES))
    index_resample = mr.low_variance_sampler(Xt, samples_p)
    resamples_x = []
    resamples_y = []
    resamples_t = []
    resamples_p = []
    
    resamples_ut = []
    resamples_occupancy_grids = []

    #print("Re-sampling")
    for i in range(SAMPLES):
        resamples_x.append(samples_x[index_resample[i]])
        resamples_y.append(samples_y[index_resample[i]])
        resamples_t.append(samples_t[index_resample[i]])
        resamples_p.append(samples_p[index_resample[i]])
        
        resamples_ut.append([ut[index_resample[i]][0], ut[index_resample[i]][1]])
        resamples_occupancy_grids.append(occupancy_grids[index_resample[i]])
    
    samples_x = resamples_x
    samples_y = resamples_y
    samples_t = resamples_t
    samples_p = resamples_p

    ut = resamples_ut
    occupancy_grids = resamples_occupancy_grids

    # End re-sampling
    #'''

for cell in occupancy_grids[g].cells:
    mcl_matrix[int(XLEN/2)+cell.x, cell.y+int(YLEN/2)] = cell.p

file_name = "./results/mcl_map.txt"
file_conn = open(file_name, 'w', encoding="utf-8")
for x in range(XLEN):
    for y in range(YLEN):
        if file_conn != None:
            file_conn.write(f'{mcl_matrix[x,y]} ')
    file_conn.write("\n")
file_conn.close()