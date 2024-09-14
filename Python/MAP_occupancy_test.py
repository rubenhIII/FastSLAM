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

# Sampling initial particles

XLEN = 500
YLEN = 500
TLEN = 0
SAMPLES = 5

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
[1,0,2,1],
[2,0,2,2],
[2,0,2,2],
[2,1,2,2],
[2,0,1,1],
[0,0,1,1],
[2,0,2,2],
[0,2,1,2],
[1,2,2,2],
[1,1,2,1],

[1,1,2,2],
[0,0,2,1],
[1,2,2,1],
[1,2,2,0],
[1,1,2,0],
[2,1,2,0],
[1,1,1,2],
[1,2,2,2],
[2,1,1,1],
[2,1,2,2],
[1,2,2,2],
[2,0,1,1],
[2,1,1,0],
[2,2,2,1],
[2,0,2,1],
[2,1,2,0],
[2,2,1,1],
[1,2,2,2],
[1,2,2,2],

[2,2,2,0],
[2,2,2,0],
[2,0,2,1],
[2,1,2,0],
[1,0,2,3],
[2,0,2,1],
[1,1,2,2],
[1,0,2,2],
[1,0,2,2],
[2,1,2,1]
]

range_vec = [
[111.34,110.98,156.65,290.25,99.69,96.01,96.78,62.72,60.73,59.51,59.68,60.28,60.66,111.73,23.12,21.44,20.75,20.44,19.79,19.98,22.04,22.36],
[109.37,109.86,210.60,101.25,95.80,97.03,94.63,61.57,58.70,57.50,57.68,57.76,58.96,108.77,23.48,21.56,20.80,20.49,19.86,20.85,21.61,21.51],
[108.17,109.21,211.84,245.30,95.39,93.45,93.02,58.52,58.16,56.03,55.87,56.32,57.13,108.51,22.84,21.49,20.85,19.98,20.25,21.30,20.80,20.79],
[107.94,216.74,222.86,96.47,93.06,91.86,91.00,57.69,55.87,54.73,54.07,55.02,54.86,107.26,22.90,21.61,20.85,20.08,20.19,20.44,22.81,22.59],
[108.82,147.27,212.27,223.22,90.89,89.28,88.37,88.20,54.06,53.03,52.41,52.67,53.25,102.52,23.53,21.40,20.75,20.00,20.15,20.48,21.90,21.92],
[110.10,207.00,226.24,278.98,90.04,86.52,86.71,86.02,52.82,50.47,50.49,50.23,50.97,101.44,23.41,21.35,20.65,20.00,20.15,20.80,21.59,21.92],
[109.23,205.83,237.61,236.36,86.33,86.42,84.40,84.05,50.73,49.12,48.41,48.57,48.76,51.59,23.12,21.45,20.75,20.05,20.20,20.08,21.87,21.97],
[112.76,149.22,145.60,3203.05,83.79,83.93,82.71,82.34,49.22,47.39,46.96,46.70,46.99,49.68,23.84,21.83,21.06,20.70,20.46,20.65,22.62,22.64],
[107.82,142.16,272.22,216.55,85.44,83.14,81.51,81.17,47.83,46.96,45.74,45.16,45.79,28.73,24.90,21.92,20.92,20.51,20.67,20.85,22.42,21.97],
[107.36,106.42,3226.29,268.96,301.48,80.73,79.70,80.33,79.64,43.90,43.48,43.17,42.82,45.33,24.83,22.11,21.30,21.01,20.70,20.91,21.51,21.61],

[106.00,139.88,207.46,334.61,228.85,80.43,79.06,77.74,77.79,43.17,42.10,41.79,41.85,27.58,24.20,22.14,21.32,20.49,20.75,20.96,21.33,21.66],
[105.35,138.26,3172.70,86.69,263.25,79.71,79.10,76.57,75.36,42.81,40.89,40.34,40.59,40.80,22.98,22.28,21.87,21.11,20.41,21.06,21.39,22.05],
[106.76,135.11,3190.52,235.86,272.58,76.27,76.32,74.76,73.57,41.74,39.62,39.10,38.62,38.98,23.51,22.78,21.97,21.21,20.56,20.43,22.16,22.26],
[105.78,107.62,215.39,270.16,75.55,73.59,73.20,72.20,71.22,40.70,37.85,37.47,37.20,36.80,38.93,23.77,25.09,49.72,22.33,21.56,23.24,22.81],
[106.12,203.57,204.08,217.05,73.02,71.29,70.88,68.98,69.01,68.82,37.22,36.46,35.74,35.95,35.74,257.34,23.92,21.51,21.27,21.45,24.71,24.94],
[106.79,139.36,211.60,264.85,70.76,68.29,67.49,66.49,66.90,67.49,37.30,35.29,34.52,34.40,25.33,22.57,21.76,21.45,20.84,23.03,25.81,25.69],
[132.36,203.95,214.58,262.05,68.50,66.75,66.35,66.85,67.21,67.67,37.52,33.96,33.97,32.93,25.43,23.03,21.81,21.11,20.80,20.60,21.27,20.94],
[105.04,136.21,207.50,199.08,231.65,65.68,65.27,66.23,99.16,73.40,69.89,33.67,32.05,31.40,26.75,23.07,21.95,21.09,21.37,20.84,22.21,22.55],
[127.53,139.72,202.18,231.85,3210.12,61.64,62.08,62.12,62.32,73.14,69.22,32.93,31.09,30.84,29.26,23.58,22.04,22.00,21.35,21.97,23.07,23.15],
[135.59,135.69,3232.29,3215.23,253.55,250.63,61.12,61.53,59.18,59.18,61.83,64.43,30.03,29.77,26.89,23.41,22.52,21.76,21.90,21.66,22.76,22.67],
[136.05,136.60,203.02,216.43,217.07,253.36,117.94,58.93,56.77,57.49,59.36,32.91,29.57,28.55,26.50,24.18,22.42,21.81,21.08,21.71,23.12,23.22],
[134.40,132.83,136.81,254.51,257.40,245.30,57.18,55.15,54.43,55.03,56.97,59.49,30.13,29.02,26.65,23.72,22.60,22.31,21.59,22.21,22.54,22.86],
[132.76,132.02,199.87,194.04,3192.92,54.11,54.09,52.98,52.19,53.59,54.97,58.58,29.69,27.89,27.06,23.89,22.67,22.31,21.33,22.26,22.81,22.93],
[136.79,194.40,192.39,192.51,55.05,53.06,53.10,52.68,50.28,50.03,52.38,54.18,29.69,28.52,29.46,24.01,22.72,21.95,22.11,22.26,22.66,22.88],
[133.10,132.42,133.44,190.98,52.79,51.59,50.78,51.28,51.84,48.11,48.76,51.54,31.50,28.67,29.15,23.98,22.83,22.12,22.23,22.00,23.02,23.12],
[128.85,130.39,134.37,222.49,225.54,54.01,51.55,50.16,49.72,46.80,46.68,49.67,51.84,29.21,28.67,25.40,23.34,22.21,21.59,22.52,23.22,23.53],
[130.61,132.79,209.97,209.37,268.79,48.05,49.01,50.37,48.14,46.06,45.52,48.91,49.80,50.92,83.37,25.00,23.05,22.23,22.42,22.64,23.34,23.34],
[131.57,129.24,131.47,234.06,47.40,45.77,45.07,46.08,48.81,47.66,47.04,47.28,49.05,50.22,29.98,80.38,22.47,22.17,22.31,23.74,24.06,24.28],
[126.89,127.46,128.52,189.46,184.23,43.97,43.29,43.32,41.95,51.04,46.48,47.09,46.53,48.36,26.34,23.44,22.66,21.92,21.20,21.80,22.60,22.93],

[126.84,125.83,129.35,263.10,48.35,40.89,88.22,40.78,38.88,41.26,45.88,44.73,45.36,45.21,47.54,26.31,24.63,21.56,21.32,21.51,23.43,23.31],
[126.22,126.40,128.76,181.19,40.83,38.59,43.75,39.19,36.80,42.60,42.41,44.68,44.52,45.58,74.89,23.79,22.52,22.12,21.92,22.48,263.82,263.41],
[128.01,126.43,132.76,181.38,39.43,37.58,39.53,37.73,34.95,37.16,38.23,49.17,44.74,43.73,66.18,25.35,22.98,22.62,25.33,22.67,22.81,22.19],
[125.47,126.09,129.24,130.37,40.25,258.97,3215.18,33.48,33.24,37.63,32.81,39.22,41.86,43.10,44.47,24.23,23.12,22.36,21.75,22.28,22.52,22.52],
[124.73,124.89,127.30,128.81,210.14,36.05,33.77,32.17,32.83,35.47,30.54,40.73,42.12,41.47,69.82,26.05,24.39,23.07,22.93,22.81,23.94,23.84],
[123.62,125.07,124.78,128.21,256.00,32.28,29.93,30.46,31.92,32.12,33.97,30.24,85.96,40.54,177.13,26.10,24.13,23.38,22.66,23.68,23.82,23.94],
[123.34,124.44,125.16,130.51,32.09,29.38,27.80,27.94,136.99,29.28,34.39,90.50,35.59,37.04,48.81,26.21,24.54,23.72,23.53,23.56,24.78,24.78],
[123.39,124.01,127.94,36.48,28.57,27.01,25.74,25.02,26.15,59.18,30.17,69.83,35.45,34.78,36.55,26.39,24.78,24.22,23.72,24.42,24.68,24.58],
[124.41,124.17,131.32,33.82,25.48,23.77,23.14,23.27,23.03,26.51,22.76,36.27,34.13,34.28,32.02,26.65,24.99,24.11,24.34,24.22,25.14,25.23],
[122.45,123.05,125.88,29.14,23.32,22.57,22.29,22.31,22.42,23.12,23.17,3192.27,24.58,32.05,31.25,27.06,24.99,24.46,24.42,24.13,24.90,24.90]
]

pos_1 = [0,0,0]
dt = 0.5

# ------ Map parameters ----#

rows = 500
cols = 500
grid_size = 5
bounds = {
    "EMPTY_CELL" : 0,
    "OBSTACLE_CELL" : 1,
    "START_CELL" : 2,
    "GOAL_CELL" : 3,
    "MOVE_CELL" : 4
}
new_map = gm.map(rows, cols)

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
        particle_grid = new_map.get_grid(sample_x, sample_y)
        #grid_particle_pos = grid.append(particle_grid[0], particle_grid[1], 0, 0)
        mcl_matrix[int(XLEN/2)+particle_grid[0], particle_grid[1]+int(YLEN/2)] = 0.25
        # -------------------------------
        # End of block occupancy update
        # -------------------------------

        range_distances = range_vec[tick_index]
        range_pos = -90
        range_angles = list(range(-90, 108, 9))
        range_angles = [x * np.pi/180.0 for x in range_angles]
        q = 1

        for s in range_distances:
            if s <= 50:
                #s = 150
                
                z_t = range_pos * np.pi / 180.0
                sensor_data = mr.likelihood_field_range_finder_model([s], [sample_x, sample_y, sample_t], [sample_x, sample_y, z_t])
    
                s_data = [sensor_data[0], sensor_data[1]]
                s_data = new_map.get_grid(s_data[0], s_data[1])
    
                # Likelihood calculation
                dist = mr.nearest_neighbour(grid, s_data[0], s_data[1])
                q = q * mr.likelihood_field_range_finder_prob(dist)
               
                # -----------------------------------
                # -- Block of occupancy map update---
                # ----------------------------------
                grid_beam_pos = grid.find(s_data[0],s_data[1])
                if grid_beam_pos == False:
                    grid_beam_pos = grid.append(s_data[0],s_data[1], 0, 0)
                beam_probs = mr.occupancy_grid_mapping(grid_beam_pos.l, [particle_grid[0], particle_grid[1], sample_t], 
                                                       [range_distances, range_angles], [grid_beam_pos.x, grid_beam_pos.y])
                grid_beam_pos.l = beam_probs[0]
                grid_beam_pos.p = beam_probs[1]
                # -------------------------------
                # End of block occupancy update
                # -------------------------------
                # This is just for a test to try to see the obstacles
                #mcl_matrix[int(XLEN/2)+s_data[0], s_data[1]+int(YLEN/2)] = 0.25
                
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

        # print(f'{ut[index_resample[i]][0]} {[0,0,0]}')
        # print(f'X: {samples_x[i]} Y: {samples_y[i]} T: {samples_t[i]} P: {samples_p[i]}')
    
    samples_x = resamples_x
    samples_y = resamples_y
    samples_t = resamples_t
    samples_p = resamples_p

    ut = resamples_ut
    occupancy_grids = resamples_occupancy_grids

    # End re-sampling
    #'''

for cell in occupancy_grids[g].cells:
    mcl_matrix[int(XLEN/2)+cell.x, cell.y+int(YLEN/2)] = 0.25

file_name = "./results/mcl_map.txt"
file_conn = open(file_name, 'w', encoding="utf-8")
for x in range(XLEN):
    for y in range(YLEN):
        if file_conn != None:
            file_conn.write(f'{mcl_matrix[x,y]} ')
    file_conn.write("\n")
file_conn.close()