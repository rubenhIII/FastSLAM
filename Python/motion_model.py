import numpy as np

def prob_dist(dist, a, b):
    if (dist == "normal"):
        val = 1 / np.sqrt(2 * np.pi * b * b) * np.exp((-1/2) * (a*a)/(b*b))
        return val
    elif (dist == "triangular"):
        val = np.max(0, (1/(np.sqrt(6))*b) - (np.abs(a)/(6*b*b)))
        return val
    
def sample_dist(dist, b):
    if (dist == "normal"):
        for i in range(1,12):
            val = random_range(b)
        return (1/2) * val
    elif (dist == "triangular"):
        return (np.sqrt(6)/2)*(random_range(b) + random_range(b))
    
def random_range(range):
    return (np.random.rand() * 2 * range) - range

def sample_motion_model_odometry(ut, xt_1):

    a1 = 0.1
    a2 = 0.1
    a3 = 0.1
    a4 = 0.1

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

    dgrot1 = drot1 - sample_dist("normal", (a1 * np.power(drot1,2)) + (a2 * np.power(dtran,2)))
    dgtran = dtran - sample_dist("normal", (a3 * np.power(dtran,2)) + (a4 * np.power(drot1,2)) + (a4 * np.power(drot2,2)))
    dgrot2 = drot2 - sample_dist("normal", (a1 * np.power(drot2,2)) + (a2 * np.power(dtran,2)))

    xp = x + dgtran * np.cos(t + dgrot1)
    yp = y + dgtran * np.sin(t + dgrot1)
    tt = t + dgrot1 + dgrot2

    return [xp,yp,tt]
   
control = [[1,0,0],[1.98,0,0]]
position = [1,0,0]

posSample = sample_motion_model_odometry(control, position)
print(f'La posición estimada es x={posSample[0]}, y={posSample[1]}, theta={posSample[2]}')