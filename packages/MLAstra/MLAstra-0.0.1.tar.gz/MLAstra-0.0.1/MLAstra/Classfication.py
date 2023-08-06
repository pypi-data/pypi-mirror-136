import numpy as np
import math
from MLAstra.Functional import sigmoid,BinaryCrossEntropy


class LogisticRegression():
    def __init__(self,n_features):
        self.n_features = n_features
        self.W = np.random.random((self.n_features,1))
        self.b = np.random.random(1)
    
    def fit(self,data,label,batch_size=None,Epochs=None,learning_rate=0.01):
        costs = []
        
        if batch_size is not None:
            n_batches = math.ceil(data.shape[0]/batch_size)
            
            for epoch in range(Epochs):
                for j in range(n_batches):

                    X1 = data[(j*n_batches):((j+1)*n_batches-1)]
                    Y1 = label[(j*n_batches):((j+1)*n_batches-1)]
                    
                    n_samples = Y1.shape[0]

                    z = np.dot(X1,self.W) + self.b
                    y_pred = sigmoid(z)
                    
                    cost = (-1/n_samples)*BinaryCrossEntropy(y_pred,Y1)
                    
                    dW = (-1/n_samples)*(np.dot(X1.T,y_pred-Y1))
                    db = (-1/n_samples)*np.sum((y_pred - Y1))
                    self.W = self.W + learning_rate*dW
                    self.b = self.b + learning_rate*db

                print("Epoch [{}]  ++++++++++++   Current Loss :- {}".format(epoch,cost))
                costs.append(cost)
            return costs
            
        else:
            X1 = data
            Y1 = label
            for epoch in range(Epochs):   
                n_samples = Y1.shape[0]
                z = np.dot(X1,self.W) + self.b
                y_pred = sigmoid(z)
                
                cost = (-1/n_samples)*BinaryCrossEntropy(y_pred,Y1)
                
                dW = (-1/n_samples)*(np.dot(X1.T,y_pred-Y1))
                db = (-1/n_samples)*np.sum((y_pred - Y1))
                self.W = self.W + learning_rate*dW
                self.b = self.b + learning_rate*db

                print("Epoch [{}]  ++++++++++++   Current Loss :- {:.4f}".format(epoch,cost))
                costs.append(cost)
            return costs
    
    def predict(self,data):
        return np.dot(data,self.W)

    def evaluate(self,test_data,test_label):
        pred_label = self.predict(test_data)
        n_samples = len(test_label)
        for i in range(n_samples):
            if pred_label[i] > 0.5:
                pred_label[i] = 1
            else:
                pred_label[i] = 0
        count = 0
        for i in range(n_samples):
            if pred_label[i]==test_label[i]:
                count += 1
        Acc = (count/n_samples)*100
        return pred_label,Acc
    