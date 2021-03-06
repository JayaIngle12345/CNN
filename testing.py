from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import pandas as pd 
import numpy as np 
import os

l1regScale = 0.7
l2regScale = 0.5

reglr = tf.contrib.layers.l1_l2_regularizer(
    scale_l1=l1regScale,
    scale_l2=l2regScale,
    scope=None
)

phaseTrain = False #Passing the argument to the layer to indicate that this not training phase
batch_size = 10
lr = 0.0001
initMethod = 2
valSetSize = 10
epochs = 1
saveDir = "sav/"
nonlnrty = tf.nn.relu
i = 19
step = 549
import random
chkLocation = saveDir+"model_e_" + str(i)+"_s_"+str(step) +".ckpt"

fileName = saveDir+"submission.csv"

f = open(fileName,"w")

f.write("id,label\n")

datasetLoc = ""

#Reading Data
trainD = pd.read_csv( datasetLoc + "train.csv", low_memory=False)
valD = pd.read_csv( datasetLoc + "val.csv", low_memory=False)
testD = pd.read_csv( datasetLoc + "test.csv", low_memory=False)

#Breaking Labels and Features

#Training
trainDnp = trainD.values
trainLabels = trainDnp[0:55001,785:786] #Label Classification
trainFeatures = trainDnp[0:55000,1:785] #Traning Input data
trainDnp = None

#Validation
valDnp = valD.values
valLabels = valDnp[0:5001,785:786] #Label Classification
valFeatures = valDnp[0:5000,1:785] #Validation Input Data

ValDnp = None

#Testing
testDnp = testD.values
testFeatures = testDnp[:,1:785] #Testing we don't have Labels

testDnp = None
## Normalizing Data

(no_of_row,no_of_col) = (np.shape(trainFeatures)) #Training Operation
(val_row,val_col) = (np.shape(valFeatures)) #Validation Operation
(test_row,test_col) = (np.shape(testFeatures)) #Validation Operation

mn = np.mean(trainFeatures,axis = 0) #Mean of training data
tiled_mn = np.tile(mn, (no_of_row, 1)) #Training : tiling up mean for substraction
val_tiled_mn = np.tile(mn,(val_row,1)) #Validation : tiling up mean for validation
test_tiled_mn = np.tile(mn,(test_row,1)) #Testing : tiling up mean for validation

st_dev = np.std(trainFeatures,axis = 0) #Standard deviation of training data
tiled_st_dev = np.tile(st_dev, (no_of_row, 1)) #Training : tiling of variance for division
val_tiled_st_dev = np.tile(st_dev,(val_row,1)) #Validation : tiling up variance for division
test_tiled_st_dev = np.tile(st_dev,(test_row,1)) #Testing : tiling up variance for division

#Normalizing Training Data
mn_shifted_data = trainFeatures - tiled_mn 
trainFeatures = mn_shifted_data/tiled_st_dev 

#Normalizing Validation Data
mn_shifted_val_d = valFeatures - val_tiled_mn
valFeatures = mn_shifted_val_d/val_tiled_st_dev

#Normalizing Testing Data
mn_shifted_test_d = testFeatures - test_tiled_mn
testFeatures = mn_shifted_test_d/test_tiled_st_dev

#Setting All the useless variables to None so that there memory can be freed

#Cleaning Area###############################

mn = None
tiled_mn = None
val_tiled_mn = None
test_tiled_mn = None

st_dev = None
tiled_st_dev = None 
val_tiled_st_dev = None
test_tiled_st_dev = None

mn_shifted_data = None 
mn_shifted_val_d = None
mn_shifted_test_d = None

trainD = None
valD = None
testD = None

trainPhase = False
##############################################
#Data set Variables are trainFeatures, valFeatures, testFeatures and truth valLabels, trainLabels

########################################################################################
################# Support Code ########################################################
######################################################################################

def transformOp(image):
    img = np.reshape(image,(28,28))
    x1 = random.randint(-2,2)
    y1 = random.randint(-2,2)
    angle = random.randint(-20,20)
    flp = random.randint(0,1)
    form = SimilarityTransform(translation=(x1, y1))
    img = warp(img, form,preserve_range=True)
    img = rotate(img,angle,preserve_range=True)
    if flp == 1:
        img = img[:, ::-1]
    return np.reshape(img,(784,))

##############################################

#Data set Variables are trainFeatures, valFeatures, testFeatures and truth valLabels, trainLabels

###################################################
#Start of the Graph TF ############################
########################################3#############

# Declaring Placeholders
features = tf.placeholder(dtype=tf.float32)
labels = tf.placeholder(dtype=tf.int32)

#Initialization Method Deciding Condition
if initMethod == 1:
    initializerUsed = tf.contrib.layers.xavier_initializer()
else:
    initializerUsed = tf.keras.initializers.he_normal()


# for input layer 
input_layer =tf.reshape(features,[-1,28,28,1]) # here 3 corresponds to RGB channel

reglr = tf.contrib.layers.l1_l2_regularizer(
    scale_l1=l1regScale,
    scale_l2=l2regScale,
    scope=None
)


#conv layer 1 
conv1 = tf.layers.conv2d(
    inputs = input_layer,
    filters = 64,
    kernel_size = [3,3],
    padding = "same",
    activation=nonlnrty,
    kernel_initializer = initializerUsed,
    name = 'conv1',
    kernel_regularizer= reglr,
    bias_regularizer = reglr
    )

# #Pooling Layer 1
pool1 = tf.layers.max_pooling2d(inputs = conv1,padding="same",pool_size = [2,2],strides = 1,name = 'pool1')

pool1Batch = tf.layers.batch_normalization(
    inputs=pool1,
    axis=-1,
    momentum=0.99,
    epsilon=0.001,
    center=True,
    scale=True,
    beta_initializer=tf.zeros_initializer(),
    gamma_initializer=tf.ones_initializer(),
    moving_mean_initializer=tf.zeros_initializer(),
    moving_variance_initializer=tf.ones_initializer(),
    beta_regularizer=None,
    gamma_regularizer=None,
    beta_constraint=None,
    gamma_constraint=None,
    training=phaseTrain,
    trainable=True,
    name=None,
    reuse=None,
    renorm=False,
    renorm_clipping=None,
    renorm_momentum=0.99,
    fused=None,
    virtual_batch_size=None,
    adjustment=None
)


#conv layer 2
conv2 = tf.layers.conv2d(
    inputs = pool1Batch,
    filters = 128,
    kernel_size = [3,3],  
    padding = "same",
    activation = nonlnrty,
    kernel_initializer = initializerUsed,
    name='conv2',
    kernel_regularizer= reglr,
    bias_regularizer = reglr
      )

#pooling layer 2
pool2 = tf.layers.max_pooling2d(inputs = conv2,padding="same",pool_size = [2,2],strides = 1,name ='pool2')

pool2Batch = tf.layers.batch_normalization(
    inputs=pool2,
    axis=-1,
    momentum=0.99,
    epsilon=0.001,
    center=True,
    scale=True,
    beta_initializer=tf.zeros_initializer(),
    gamma_initializer=tf.ones_initializer(),
    moving_mean_initializer=tf.zeros_initializer(),
    moving_variance_initializer=tf.ones_initializer(),
    beta_regularizer=None,
    gamma_regularizer=None,
    beta_constraint=None,
    gamma_constraint=None,
    training=phaseTrain,
    trainable=True,
    name=None,
    reuse=None,
    renorm=False,
    renorm_clipping=None,
    renorm_momentum=0.99,
    fused=None,
    virtual_batch_size=None,
    adjustment=None
)



#convo layer 3
conv3 = tf.layers.conv2d(
    inputs = pool2Batch,
    filters = 256,
    kernel_size = [3,3],  
    padding = "same",
    activation = nonlnrty,
    kernel_initializer = initializerUsed,name = 'conv3',
    kernel_regularizer= reglr,
    bias_regularizer = reglr
      )

#convo layer 4
conv4 = tf.layers.conv2d( inputs = conv3,
    filters = 256,
    kernel_size = [3,3],  
    padding = "same",
    activation = nonlnrty,
    kernel_initializer = initializerUsed ,name = 'conv4',
    kernel_regularizer= reglr,
    bias_regularizer = reglr
     )

conv4Batch = tf.layers.batch_normalization(
    inputs=conv4,
    axis=-1,
    momentum=0.99,
    epsilon=0.001,
    center=True,
    scale=True,
    beta_initializer=tf.zeros_initializer(),
    gamma_initializer=tf.ones_initializer(),
    moving_mean_initializer=tf.zeros_initializer(),
    moving_variance_initializer=tf.ones_initializer(),
    beta_regularizer=None,
    gamma_regularizer=None,
    beta_constraint=None,
    gamma_constraint=None,
    training=phaseTrain,
    trainable=True,
    name=None,
    reuse=None,
    renorm=False,
    renorm_clipping=None,
    renorm_momentum=0.99,
    fused=None,
    virtual_batch_size=None,
    adjustment=None
)


conv5 = tf.layers.conv2d( inputs = conv4Batch,
    filters = 384,
    kernel_size = [3,3],  
    padding = "same",
    activation = nonlnrty,
    kernel_initializer = initializerUsed ,name = 'conv5',
    kernel_regularizer= reglr,
    bias_regularizer = reglr
     )


#pool layer 3
pool3 = tf.layers.max_pooling2d(inputs = conv5,padding="same",pool_size = [2,2],strides = 1,name = 'pool3')

pool3Batch = tf.layers.batch_normalization(
    inputs=pool3,
    axis=-1,
    momentum=0.99,
    epsilon=0.001,
    center=True,
    scale=True,
    beta_initializer=tf.zeros_initializer(),
    gamma_initializer=tf.ones_initializer(),
    moving_mean_initializer=tf.zeros_initializer(),
    moving_variance_initializer=tf.ones_initializer(),
    beta_regularizer=None,
    gamma_regularizer=None,
    beta_constraint=None,
    gamma_constraint=None,
    training=phaseTrain,
    trainable=True,
    name=None,
    reuse=None,
    renorm=False,
    renorm_clipping=None,
    renorm_momentum=0.99,
    fused=None,
    virtual_batch_size=None,
    adjustment=None
)


#Making pool3 flat for the purpose of sending it to dense layer
pool3_flat = tf.reshape(pool3Batch,[-1,28*28*384])

fc1 = tf.layers.dense(inputs=pool3_flat, units=1024, activation=nonlnrty,kernel_initializer = initializerUsed,kernel_regularizer = reglr,
    bias_regularizer = reglr,name = 'fc1')

#fully connected 2
fc2 = tf.layers.dense(inputs=fc1,units = 1024,activation =nonlnrty,kernel_regularizer= reglr,
    bias_regularizer = reglr,kernel_initializer = initializerUsed,name = 'fc2')


# ##############BATCH NORMALISATION IS LEFT HERE ####################################
normalizedBatch = tf.layers.batch_normalization(
    inputs=fc2,
    axis=-1,
    momentum=0.99,
    epsilon=0.001,
    center=True,
    scale=True,
    beta_initializer=tf.zeros_initializer(),
    gamma_initializer=tf.ones_initializer(),
    moving_mean_initializer=tf.zeros_initializer(),
    moving_variance_initializer=tf.ones_initializer(),
    beta_regularizer=None,
    gamma_regularizer=None,
    beta_constraint=None,
    gamma_constraint=None,
    training=phaseTrain,
    trainable=True,
    name=None,
    reuse=None,
    renorm=False,
    renorm_clipping=None,
    renorm_momentum=0.99,
    fused=None,
    virtual_batch_size=None,
    adjustment=None
)

do4 = tf.layers.dropout(
    inputs = normalizedBatch,
    rate=0.4,
    noise_shape=None,
    seed=None,
    training=phaseTrain,
    name=None
)


update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)

#Last Layer // Output Layer
logits = tf.layers.dense(inputs = do4,units =10,kernel_initializer = initializerUsed,name = 'logits',kernel_regularizer= reglr,
    bias_regularizer = reglr)

#Getting Prediction Labels as tensor 1d
predictedLabels = tf.argmax(input=logits, axis=1)
pll = tf.cast(predictedLabels,tf.int32)
c = tf.equal(pll,labels[:,0]) 
correctCount = tf.reduce_sum(tf.cast(c, tf.int32)) #Getting the count of correct predicition

#For Training Core : one_hot, Loss, optimizer, training
onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=10)
loss = tf.losses.softmax_cross_entropy(onehot_labels,logits)
tf.control_dependencies(update_ops)
optimizer = tf.train.RMSPropOptimizer(lr,momentum=0.08)
training = optimizer.minimize(loss)


#For saving the graph Variables
saver = tf.train.Saver()
sess = tf.Session()
#sess : Session, chkLocation : Location of checkpoint
saver.restore(sess,chkLocation)




totalSteps = len(testFeatures)

for step in range(0,totalSteps):
    #Retriving a Batch for process
    batchD = testFeatures[step]
    print(step)
    TcorrectP = sess.run([predictedLabels],feed_dict={features:batchD})
    f.write(str(step)+" ,"+str(int(TcorrectP[0]))+"\n")   

f.close()
