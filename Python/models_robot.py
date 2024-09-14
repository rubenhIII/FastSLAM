import numpy as np
import scipy.stats
import random
import time
from sklearn.cluster import KMeans

'''The parameter ut is a list of two list: 
1. The position of perceived by the robot before a movement.
2.The posteriori estimation for the robot position calculated from the odometry data.
The parameter xt_1 is the robot's global posture.
'''
def odometry_motion_model(ut, xt_1):
    a1 = 0.001
    a2 = 0.001
    a3 = 0.001
    a4 = 0.001
	
    xb = ut[0][0]
    yb = ut[0][1]
    tb = ut[0][2]
	
    xbp = ut[1][0]
    ybp = ut[1][1]
    tbp = ut[1][2]
    
    x = xt_1[0]
    y = xt_1[1]
    t = xt_1[2]
	
    drot1 = np.arctan2(ybp - yb, xbp - xb) - tb
    dtran = np.sqrt(np.power(xb - xbp,2) + np.power(yb - ybp, 2))
    drot2 = tbp - tb - drot1
	
    ##Ask to Antonio what is the difference between the built-in function and the scripted one!!
    dgrot1 = drot1 - sample_dist("normal", (a1 * np.power(drot1,2)) + (a2 * np.power(dtran,2)))
    dgtran = dtran - sample_dist("normal", (a3 * np.power(dtran,2)) + (a4 * np.power(drot1,2)) + (a4 * np.power(drot2,2)))
    dgrot2 = drot2 - sample_dist("normal", (a1 * np.power(drot2,2)) + (a2 * np.power(dtran,2)))
	
    xp = x + dgtran * np.cos(t + dgrot1)
    yp = y + dgtran * np.sin(t + dgrot1)
    tt = t + dgrot1 + dgrot2
    #print(f'xp={xp} yp={yp} tt={tt * 180 / np.pi}')
    return [xp,yp,tt]

def kinematic_model(wheels_ticks, drive_time, t_old):
    ticks_left = tick_means(wheels_ticks)[0]
    ticks_right = tick_means(wheels_ticks)[1]
    pulses_per_turn = 20
    wheel_radius = 3.48
    rear_length = 20
    x_icr = 1
    wl = 2 * np.pi * ((ticks_left / pulses_per_turn) / drive_time) #RPS -> rad/s
    wr = 2 * np.pi * ((ticks_right / pulses_per_turn) / drive_time)
    vx = wheel_radius * ((wl + wr) / 2)
    wz = wheel_radius * ((wr - wl) / rear_length)
    x = ((np.cos(t_old) * vx) + (x_icr * np.sin(t_old) * wz)) * drive_time
    y = ((np.sin(t_old) * vx) + (-x_icr * np.cos(t_old) * wz)) * drive_time
    t = wz * drive_time #Radians
    #print(f'x={x} y={y} orientation={t * 180 / np.pi}')
    return [x,y,t]
	
def tick_means(wheels_ticks):
	ticks_left = np.mean(np.array([wheels_ticks[0], wheels_ticks[2]]))
	ticks_right = np.mean(np.array([wheels_ticks[1], wheels_ticks[3]]))
	return [ticks_left,ticks_right]

def sample_normal_dist(b2):
	return np.random.normal(0, b2, 1)

def sample_dist(dist, b):
    if (dist == "normal"):
        val = 0
        b = np.power(b, 2)
        for i in range(13):
            val = val + random_range(np.sqrt(b))
        return (1/2) * val
    elif (dist == "triangular"):
        return (np.sqrt(6)/2)*(random_range(b) + random_range(b))
    
def random_range(range):
    return ((np.random.rand() * 2) - 1) * range

def kmeans_pos(positions_array, clusters):
     kmeans = KMeans(n_clusters=clusters, random_state=0, n_init="auto").fit(positions_array)
     return kmeans.cluster_centers_

def sample_range_sensor(orientation, distance):
    p = (distance + sample_dist("normal", 1))
    p_x = np.sin(orientation) * p
    p_y = np.cos(orientation) * p
    p_theta = orientation
    measurement = [p_x, p_y, p_theta]
    return measurement


def likelihood_field_range_finder_model(zt, xt, zxt):
     for z in zt:
          x = xt[0]
          y = xt[1]
          theta = xt[2]

          x_sensor = zxt[0]
          y_sensor = zxt[1]
          theta_sensor = zxt[2]

          xzt = x + x_sensor * np.cos(theta) - y_sensor * np.sin(theta) + z * np.cos(theta + theta_sensor)
          yzt = y + y_sensor * np.cos(theta) + x_sensor * np.sin(theta) + z * np.sin(theta + theta_sensor)
          
          ## The functions to calculate the likelihood were moved to another function.
          ## This with the purpose of use the xzt and yzt to plot the obstacles in the map.
          #dist = nearest_neighbour(xzt, yzt, m)
          #q = q * (zhit * sample_dist("normal", shit) + (zran / zmax))

          measurement = [xzt, yzt]

     return measurement

def likelihood_field_range_finder_prob(dist):
     # Intrinsect Error Parameters 
     shit = 0.5
     zhit = 0.9
     zran = 42
     zmax = 150

     q = zhit * scipy.stats.norm(0, shit).pdf(dist) + (zran / zmax)

     return q

def low_variance_sampler(Xt, Wt):
    random.seed(time.time())
    X_sample = []
    M = len(Xt)
    r = random.uniform(0, 1/M)
    i = 0
    c = Wt[i]

    for m in range(1, M+1):
        U = r + (m - 1) * 1 / M
        while U > c and i < M - 1:
            i = i + 1
            c = c + Wt[i]
        X_sample.append(Xt[i])
        i = 0
        c = Wt[i]
    
    return X_sample


def nearest_neighbour(grid, xzt, yzt):
        dist = np.inf
        for cell in grid.cells:
            dist_calc = np.sqrt(np.power(xzt - cell.x, 2) + np.power(yzt - cell.y, 2))
            if dist_calc < dist:
                dist = dist_calc
        return dist

def inverse_sensor_model(pos_particle, pos_cell, zt):
    
    PM1 = 0.25
    PM0 = 0.75
    l0 = np.log(PM1/PM0)
    locc = np.log(0.8/0.2)
    lfree = np.log(0.2/0.8)

    zmax = 150
    alpha = 20
    beta = 5 * np.pi/180 

    xi = pos_cell[0]
    yi = pos_cell[1]

    x = pos_particle[0]
    y = pos_particle[1]
    theta = pos_particle[2]

    r = np.sqrt(np.power(xi - x, 2) + np.power(yi - y, 2))
    phi = np.arctan2(yi - y, xi - x) - theta

    k = np.argmin([phi - z for z in zt[1]])
    
    if r > min(zmax, zt[0][k] + alpha/2) or abs(phi - zt[1][k]) > beta/2:
        #print("l0")
        return l0
    if zt[0][k] < zmax and abs(r - zt[0][k]) < alpha/2:
        #print("locc")
        return locc
    if r <= zt[0][k]:
        #print("lfree")
        return lfree

def occupancy_grid_mapping(lt_i, pos_particle, zt, pos_cell):
    PM1 = 0.25
    PM0 = 0.75
    l0 = np.log(PM1/PM0)
    lti = lt_i + inverse_sensor_model(pos_particle, pos_cell, zt) - l0
    occ_prob = 1 - (1 / (1 + np.exp(lti)))
    return[lti, occ_prob]