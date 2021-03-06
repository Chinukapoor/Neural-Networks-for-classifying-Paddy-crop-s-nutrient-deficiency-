#import tensorflow as tf
import skimage
from skimage import data
import os
import numpy as np
import matplotlib.pyplot as plt
from skimage import transform
import tensorflow as tf

def load_data(data_directory):
    directories = [d for d in os.listdir(data_directory)
                   if os.path.isdir(os.path.join(data_directory, d))]
    labels = []
    images = []
    for d in directories:
        label_directory = os.path.join(data_directory, d)
        file_names = [os.path.join(label_directory, f)
                      for f in os.listdir(label_directory)
                      if f.endswith(".jpg")]
        for f in file_names:
            images.append(skimage.data.imread(f))
            labels.append(int(d))
    return images, labels

ROOT_PATH_1 = "/home/akapoor/Downloads/"
ROOT_PATH_2 = "/home/akapoor/Downloads/"
train_data_directory = os.path.join(ROOT_PATH_1, "crop_images_train")
test_data_directory = os.path.join(ROOT_PATH_2, "crop_images_test")

images, labels = load_data(train_data_directory)
#print (images)
#images = np.array(images_list)
print (len(images))
#print(images.size)
print (images[112])

labels = np.array(labels)
print(labels.size)
print(len(set(labels)))

plt.hist(labels,4)
plt.show()

crop_types = [3, 22, 36, 100]



images28 = [transform.resize(image, (28, 28)) for image in images]
from skimage.color import rgb2gray
images28 = np.array(images28)
#images28 = rgb2gray(images28)

for i in range(len(crop_types)):
    plt.subplot(1, 4, i+1)
    plt.axis('off')
    plt.imshow(images28[crop_types[i]])
    plt.subplots_adjust(wspace=0.5)

plt.show()



# Initialize placeholders
x = tf.placeholder(dtype = tf.float32, shape = [None, 28, 28])
y = tf.placeholder(dtype = tf.int32, shape = [None])

# Flatten the input data
images_flat = tf.contrib.layers.flatten(x)

# Fully connected layer
logits = tf.contrib.layers.fully_connected(images_flat,4, tf.nn.relu)

# Define a loss function
loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels = y,
                                                                    logits = logits))
# Define an optimizer
train_op = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

# Convert logits to label indexes
correct_pred = tf.argmax(logits, 1)

# Define an accuracy metric
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))
#print("images_flat: ", images_flat)
#print("logits: ", logits)
#print("loss: ", loss)
#print("predicted_labels: ", correct_pred)
tf.set_random_seed(1234)
sess = tf.Session()
sess.run(tf.global_variables_initializer())

for i in range(201):
        print('EPOCH', i)
        _, accuracy_val = sess.run([train_op, accuracy], feed_dict={x: images28, y: labels})
        if i % 10 == 0:
            print("Loss: ", loss)
        print('DONE WITH EPOCH')
import random

# Pick 10 random images
sample_indexes = random.sample(range(len(images28)), 10)
sample_images = [images28[i] for i in sample_indexes]
sample_labels = [labels[i] for i in sample_indexes]

# Run the "correct_pred" operation
predicted = sess.run([correct_pred], feed_dict={x: sample_images})[0]

# Print the real and predicted labels
#print(sample_labels)
#print(predicted)

# Display the predictions and the ground truth visually.
fig = plt.figure(figsize=(10, 10))
for i in range(len(sample_images)):
    truth = sample_labels[i]
    prediction = predicted[i]
    plt.subplot(5, 2, 1 + i)
    plt.axis('off')
    color = 'green' if truth == prediction else 'red'
    plt.text(40, 10, "Truth:        {0}\nPrediction: {1}".format(truth, prediction),
             fontsize=12, color=color)
    plt.imshow(sample_images[i], cmap="gray")

plt.show()



test_images, test_labels = load_data(test_data_directory)
print ("length of test labels:",float(len(test_labels)))
# Transform the images to 28 by 28 pixels
test_images28 = [transform.resize(image, (28, 28)) for image in test_images]

# Convert to grayscale
test_images28 = rgb2gray(np.array(test_images28))

# Run predictions against the full test set.
predicted = sess.run([correct_pred], feed_dict={x: test_images28})[0]
# Calculate correct matches
match_count = float(sum([int(y == y_) for y, y_ in zip(test_labels, predicted)]))
print ("correctly predicted:",match_count)
#print (len(test_labels))
# Calculate the accuracy
final_accuracy = match_count/(len(test_labels))
print ("Accuracy:",final_accuracy)

