# encoding: UTF-8
# original source : https://github.com/GoogleCloudPlatform/tensorflow-without-a-phd/tree/master/tensorflow-mnist-tutorial
# 2018.12 : modified by Seungkwon Lee(kahnlee@naver.com)
import os,sys
import tensorflow as tf
import mnistdata
import math
print("Tensorflow version " + tf.__version__)
import matplotlib.pyplot as plt
import numpy as np
 
from datetime import datetime

def get_logdir() :
	now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
	root_logdir = './cnn_logs'
	logdir = "{}/run-{}/".format(root_logdir, now)
	return logdir

## RnadonState 할당으로 고정.
# tf.set_random_seed(0)

# neural network with 1 layer of 10 softmax neurons
#
# · · · · · · · · · ·       (input data, flattened pixels)       X [batch, 784]        # 784 = 28 * 28
# \x/x\x/x\x/x\x/x\x/    -- fully connected layer (softmax)      W [784, 10]     b[10]
#   · · · · · · · ·                                              Y [batch, 10]

# The model is:
#
# Y = softmax( X * W + b)
#              X: matrix for 100 grayscale images of 28x28 pixels, flattened (there are 100 images in a mini-batch)
#              W: weight matrix with 784 lines and 10 columns
#              b: bias vector with 10 dimensions
#              +: add with broadcasting: adds the vector to each line of the matrix (numpy)
#              softmax(matrix) applies softmax on each line
#              softmax(line) applies an exp to each value then divides by the norm of the resulting line
#              Y: output matrix with 100 lines and 10 columns

# Download images and labels into mnist.test (10K images+labels) and mnist.train (60K images+labels)
mnist = mnistdata.read_data_sets("data", one_hot=True, reshape=False)

# input X: 28x28 grayscale images, the first dimension (None) will index the images in the mini-batch
X = tf.placeholder(tf.float32, [None, 28, 28, 1])
# correct answers will go here
Y_ = tf.placeholder(tf.float32, [None, 10])
# weights W[784, 10]   784=28*28
W = tf.Variable(tf.zeros([784, 10]))
# biases b[10]
b = tf.Variable(tf.zeros([10]))

# flatten the images into a single line of pixels
# -1 in the shape definition means "the only possible dimension that will preserve the number of elements"
XX = tf.reshape(X, [-1, 784])

# The model
Y = tf.nn.softmax(tf.matmul(XX, W) + b)

# loss function: MSE
loss = tf.reduce_mean(tf.squared_difference(Y, Y_)) * 1000


# accuracy of the trained model, between 0 (worst) and 1 (best)
correct_prediction = tf.equal(tf.argmax(Y, 1), tf.argmax(Y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# training, learning rate = 0.005
train_step = tf.train.GradientDescentOptimizer(0.005).minimize(loss)


#------------- tensorboard
# Create a summary to monitor cost & accuracy
tf.summary.scalar("loss", loss)
tf.summary.scalar("accuracy", accuracy)
# Merge all summaries into a single op
merged_summary_op = tf.summary.merge_all()

# create tensorboard writer object
log_folder = get_logdir()
train_log_folder = os.path.join(log_folder,'train')
test_log_folder = os.path.join(log_folder,'test')

train_summary_writer = tf.summary.FileWriter(train_log_folder, graph=tf.get_default_graph())
test_summary_writer = tf.summary.FileWriter(test_log_folder, graph=tf.get_default_graph())

# init
init = tf.global_variables_initializer()

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)

sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))

# sess = tf.Session()
sess.run(init)


# run
print("change --- GPU usage options - 50% ")
for i in range(2000 + 1) :

	batch_X, batch_Y = mnist.train.next_batch(100)
	a, c = sess.run([accuracy, loss], feed_dict={X : batch_X, Y_ : batch_Y})
	print("training : ", i, ' accuracy = ', '{:7.4f}'.format(a), ' loss = ', c)

	# write tensorboard log
	if i % 10 == 0 :
		summary = sess.run(merged_summary_op, feed_dict={X: batch_X, Y_: batch_Y})
		train_summary_writer.add_summary(summary, i)

	a, c = sess.run([accuracy, loss], feed_dict={X: mnist.test.images, Y_: mnist.test.labels})
	print("testing  : ",i, ' accuracy = ', '{:7.4f}'.format(a), ' loss = ', c)

	# write tensorboard log
	if i % 10 == 0 :
		summary = sess.run(merged_summary_op, feed_dict={X: mnist.test.images, Y_: mnist.test.labels})
		test_summary_writer.add_summary(summary, i)

	sess.run(train_step, feed_dict={X : batch_X, Y_ : batch_Y} )

# close summary writer object
train_summary_writer.close()
test_summary_writer.close()