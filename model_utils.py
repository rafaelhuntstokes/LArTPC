"""
This code actually creates the CNN model, with the architecture defined in CNN model class. ExtraUtils is used to 
perform the training,testing and validation steps. 
"""

import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
import tensorflow as tf
from tensorflow.keras import Model 
from tensorflow.keras.layers import (Dense, Flatten, Conv2D, MaxPool2D,
                                        BatchNormalization)
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.optimizers import SGD, Adam 
import numpy as np 

class ExtraUtils(Model):
    """
    Class performs test, train and validation steps. Also contains functions to return the model weights.
    """

    def __init__(self, optimizer, loss_calc):
        super(ExtraUtils, self).__init__()
        self.optimizer = optimizer()
        self.loss_calc = loss_calc()
        self.bn_idxs = None 
        
    def train_step(self, images, labels):
        grads, loss, preds = self.get_grads_loss_preds(images, labels)
        self.optimizer.apply_gradients(zip(grads, self.trainable_variables))
        
        acc = np.mean(np.argmax(preds.numpy(), axis=0) 
                        == np.argmax(labels, axis=0))
        return acc, loss.numpy()
        
    def get_grads_loss_preds(self, images, labels):
        with tf.GradientTape() as tape:
            predictions = self.fwd_train(images)
            loss = self.loss_calc(labels, predictions)
            
        gradients = tape.gradient(loss, self.trainable_variables)
        return gradients, loss, predictions
        
    def train(self, client_data, B):
        x = client_data[0] 
        y = client_data[1]
        b_pr_e = x.shape[0] // B 
        
        for b in range(b_pr_e):
            self.train_step(x[b*B:(b+1)*B], y[b*B:(b+1)*B])
        if b_pr_e * B < x.shape[0]:
            self.train_step(x[b_pr_e*B:], y[b_pr_e*B:])
              
    def _test_xy(self, x, y):
        preds = self.fwd_test(x)
        loss = self.loss_calc(y, preds).numpy()
        acc = np.mean(np.argmax(preds.numpy(), axis=1) 
                        ==  np.argmax(y, axis=1))
        return loss, acc, preds 
            
    def test(self, x_vals, y_vals, B):
        pred_list = []
        b_pr_t = x_vals.shape[0] // B 
        avg_err = 0.0 
        avg_acc = 0.0 
        tot_samples = 0
        for b in range(b_pr_t):
            loss, acc, preds = self._test_xy(x_vals[b*B:(b+1)*B], y_vals[b*B:(b+1)*B])
            avg_err += loss
            avg_acc += acc 
            tot_samples += 1
            pred_list.append(preds)
        if b_pr_t * B < x_vals.shape[0]:
            loss, acc, preds = self._test_xy(x_vals[b_pr_t*B:], y_vals[b_pr_t*B:])
            avg_err += loss 
            avg_acc += acc 
            tot_samples += 1 
            pred_list.append(preds)
        return avg_err / tot_samples, avg_acc / tot_samples, pred_list

class CNNModel(ExtraUtils):

    def __init__(self, optimizer, loss_calc, outputs, activation):
        """ 
        The CNN model layers are created here. 
        """
        super(CNNModel, self).__init__(optimizer, loss_calc) 
        self.conv1 = Conv2D(32, 3, activation='relu')
        self.pool1 = MaxPool2D((2,2), (2,2))
        self.conv2 = Conv2D(64, 3, activation='relu')
        self.pool2 = MaxPool2D((2,2), (2,2))
        self.flatten = Flatten()
        self.d1 = Dense(512, activation='relu')
        if activation == 'sig':
            self.d2 = Dense(outputs, activation='sigmoid')
        else:
            self.d2 = Dense(outputs, activation='softmax')
        self.layer_list = [self.conv1, self.conv2,
                            self.d1, self.d2]

    def fwd_train(self, x):
        a = self.conv1(x)
        a = self.pool1(a)
        a = self.conv2(a)
        a = self.pool2(a)
        a = self.flatten(a)
        a = self.d1(a)
        return self.d2(a)
        
    def fwd_test(self, x):
        a = self.conv1(x)
        a = self.pool1(a)
        a = self.conv2(a)
        a = self.pool2(a)
        a = self.flatten(a)
        a = self.d1(a)
        return self.d2(a)
        