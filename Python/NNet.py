import pandas as pd
import numpy as np


nnet_weights = [[[1.12846128585199, -0.998218150764362, 1.70157752061675, 
-0.845785135302045, -1.80278380900134, -0.160269744192874], [-0.784176702494469, 
-1.80924945760016, -0.694622034431047, -0.984616327092938, 2.39361375547711, 
-0.0233550699813659], [1.46270080434808, 0.59738160382271, 0.841581923909903, 
-0.133704375218588, -1.59646245453242, 0.589281510064795], [0.625449798883621, 
1.62141424125264, -0.544456760034232, -0.999588796664905, -0.276392490772094, 
1.34638182528466], [-1.11082452261607, 0.656599353622009, 0.544105288990932, 
1.10689198524347, -0.843856863152368, 0.59538410856198]], 
[0.830274925601147, 0.328224587291397, -0.274024351148932, 
    -1.3577493618754, 0.376450864044074, 0.466917061832276]]

stats = {"w1" : {"mean" : 23.95707, "sd": 15.11511}, "w2" : {"mean" : 22.81061, "sd": 14.70631}, 
         "w3" : {"mean" :30.04040, "sd": 16.77893},"w4" : {"mean" : 26.33081, "sd": 15.87161}, 
         "pwm" : {"mean" :162.43687, "sd": 27.98614}, "time" : {"mean": 0.3237500, "sd": 0.1207875}}

def logistic(x):
    return (1/(1 + np.exp(-x)))

def normalize(wheels_data):
    x = wheels_data
    x.iloc[0] = (x.iloc[0] - stats["w1"]["mean"]) / stats["w1"]["sd"]
    x.iloc[1] = (x.iloc[1] - stats["w2"]["mean"]) / stats["w2"]["sd"]
    x.iloc[2] = (x.iloc[2] - stats["w3"]["mean"]) / stats["w3"]["sd"]
    x.iloc[3] = (x.iloc[3] - stats["w4"]["mean"]) / stats["w4"]["sd"]
    #x.iloc[4] = (x.iloc[4] - stats["time"]["mean"]) / stats["time"]["sd"]
    x.iloc[4] = (x.iloc[4] - stats["pwm"]["mean"]) / stats["pwm"]["sd"]
    return x

def eval_NN(x):
    layers = len(nnet_weights)
    for L in range(layers):
        X = pd.concat([pd.Series([1]), x])
        Y = np.transpose(nnet_weights[L])
        if L == (layers-1):
            x = np.dot(X, Y)
        else:
            x = pd.DataFrame(logistic(np.dot(X, Y)))
            x = x[0]
    return x

def test_from_file():
    file_test = './NNet/data_test.csv'
    data_test = pd.read_csv(file_test).drop(["id", "d", "m1", "m2"], axis=1)
    x = pd.DataFrame(data_test.iloc[1])[1]
    eval_NN(x, nnet_weights)