import numpy  as np


########################### SIGMOID ACTIVATION FUNCTION #########################
def sigmoid(x):
    return (1/(1+np.exp(-(x))))







########################## BINARY CROSS ENTROPY LOSS FUNCTION #######################
def BinaryCrossEntropy(y_pred,y_true):
    return np.sum((y_true.T * np.log(y_pred)) + ((1-y_true).T * np.log(1 - y_pred)))