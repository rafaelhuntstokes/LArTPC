from PIL import Image
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
import numpy as np
import matplotlib.pyplot as plt
from model_utils import CNNModel, BigCNNModel
import tensorflow as tf
from tensorflow.keras.losses import CategoricalCrossentropy as CatCrossEnt
from tensorflow.keras.optimizers import SGD, Adam
from scipy.stats import sem
from sklearn.metrics import confusion_matrix
import sklearn.metrics 
import seaborn as sn 
import pandas as pd 
import time 
np.random.seed(0)
tf.random.set_seed(0)

def load_images(folder, max_ims, image_size):
    fnames = [f for f in os.listdir(folder) if f.endswith('.jpeg')]
    np.random.shuffle(fnames)
    fnames = fnames[:max_ims]

    tot_imgs = min(len(fnames), max_ims)
    imgs = np.zeros((tot_imgs, image_size[0], image_size[1]), dtype=np.float32)
    labels = np.zeros((tot_imgs, 2), dtype=np.float32)

    noise_label = np.array([1, 0], dtype=np.float32)
    feat_label = np.array([0, 1], dtype=np.float32)

    for (i, fname) in enumerate(fnames):
        img = np.array(Image.open(folder+'/'+fname).resize(image_size))
        
        imgs[i] = img[:,:][:,:]
        labels[i] = feat_label if 'sn' in fname else noise_label

    imgs = imgs.reshape((max_ims, image_size[0], image_size[0], 1))
    imgs /= np.amax(imgs)

    return (imgs, labels)


def split_data_train_valid_test(data, train_frac, valid_frac, test_frac):
    assert train_frac + valid_frac + test_frac == 1.0
    tot_samples = data[0].shape[0]
    train_idx = int(tot_samples * train_frac)
    valid_idx = train_idx + int(tot_samples * valid_frac)

    train = (data[0][:train_idx], data[1][:train_idx])
    valid = (data[0][train_idx:valid_idx], data[1][train_idx:valid_idx])
    test = (data[0][valid_idx:], data[1][valid_idx:])

    return train, valid, test


def shuffle_data(data):
    ord = np.random.permutation(data[0].shape[0])
    return (data[0][ord], data[1][ord])



def main(optimizer, epochs, batch, activation, all_data):
    IMG_SIZE = (100,100)
    NUM_IMGS = 4000
    EPOCHS = epochs 
    BATCH_SIZE = batch 
    #FOLDER = './'+path
    TRAIN_FRAC = 0.6
    VALID_FRAC = 0.2
    TEST_FRAC = 0.2
    
    accuracy = []
    
    
    
    all_data = shuffle_data(all_data)
    train, valid, test = split_data_train_valid_test(   all_data, TRAIN_FRAC,
                                                        VALID_FRAC, TEST_FRAC)
    
    model = CNNModel(optimizer, CatCrossEnt, 2, activation)
    print('Training...')
    prev_acc = 0
    count = 0  
    for e in range(EPOCHS):
        model.train(shuffle_data(train), BATCH_SIZE)
        err, acc, preds = model.test(valid[0], valid[1], BATCH_SIZE)
        print('Epoch {}/{}, valid err = {:.2f}, valid acc = {:.2f}'
                    .format(e, EPOCHS, err, acc))
        accuracy.append(acc)

        # if acc > prev_acc:
        #     count = 0 
        # else: 
        #     count += 1
        # if count == 3:
        #     print('No longer improving - > moving to test') 
        #     break  
        # prev_acc = acc
    err2, acc2, preds = model.test(test[0], test[1], BATCH_SIZE)
    
    # obtain predicted labels 
    preds = [val for sublist in preds for val in sublist]
    preds = np.argmax(preds, axis = 1)
    actual = np.argmax(test[1], axis = 1)
    confusion = confusion_matrix(actual, preds)
    
    print('test accuracy:', acc2)

    
    return acc2, err2, confusion 

if __name__ == '__main__':
    epochs = 10
    batches = 32 

    test_acc = []
    test_acc_error = []
    test_err = [] 
    test_err_error = []
    tests =[5,10,15,20,25,30,35,40,45,50,60,70,80,90,100,200,300,400,500,1000]
    #tests = [5,5,5]
    data = ['radiation_test{}'.format(i) for i in tests]
    
    start = time.time()
    for i in range(len(data)):
        res_acc = []
        res_err = [] 
        confusion = np.zeros((2,2))
        print('Loading images...')
        all_data = load_images('./'+data[i], 1000, (100,100))
        for j in range(10):
            acc, err, confusion2 = main(Adam, epochs, batches, 'softmax', all_data)
            res_acc.append(acc)
            res_err.append(err)
            confusion += confusion2
            print('COMPLETED {} run {}\nTime: {}'.format(data[i], j, (time.time() - start) ))
        
        # compute the averages and error bars 
        av_acc = sum(res_acc)/len(res_acc)
        av_err = sum(res_err)/len(res_err)
        sem_acc = sem(res_acc)
        sem_err = sem(res_err)
        
        test_acc.append(av_acc)
        test_acc_error.append(sem_acc)
        test_err.append(av_err)
        test_err_error.append(sem_err)

        # make a pretty confusion matrix 
        confusion = sklearn.preprocessing.normalize(confusion, norm = 'l1')
        df_cm = pd.DataFrame(confusion, index = [i for i in ['sn', 'noise']], columns = [i for i in ['sn', 'noise']])
        df_cm = df_cm.round(2)
        plt.figure(figsize = (10,7))
        sn.heatmap(df_cm, annot=True, cmap="YlGnBu") 
        plt.title('Confusion Matrix for Rad{}'.format(tests[i]))
        plt.xlabel('Predicted Class')
        plt.ylabel('Known Class')
        plt.savefig('./confusions/rad{}'.format(tests[i]))
        plt.close()
    end = time.time()
    took = end - start 
    print('TOTAL TIME', took)
    plt.figure()
    plt.errorbar(tests, test_acc, yerr = test_acc_error, ecolor = 'r', capsize = 5)
    plt.title('Affect of Increasing K-42 Activity on Test Accuracy')
    plt.xlabel('K-42 Activity (per module per microsecond)')
    plt.ylabel('Test Accuracy')
    plt.savefig('./confusions/graph')
    
    np.save('./results_acc_reruns', test_acc)
    np.save('./results_err_reruns', test_err)
    np.save('./results_errorbars', test_acc_error)
    
