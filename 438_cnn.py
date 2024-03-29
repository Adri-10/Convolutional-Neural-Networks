# -*- coding: utf-8 -*-
"""438-CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sGM6zO79OhpZrVU-XTYsYR0KyOWOoJtE
"""

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

! kaggle datasets download tongpython/cat-and-dog

! unzip /content/cat-and-dog.zip

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import pandas as pd
import cv2
import os
import re
import PIL
import tensorflow as tf

from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, Flatten, Dense, Dropout

from time import perf_counter, sleep

directory_train = '/content/training_set/training_set'
directory_validation = '/content/test_set/test_set'

class_names = os.listdir(directory_train)
class_names

category_count = []

for root, dirs, files in os.walk(directory_train):
    for dir_path in dirs:
        category_count.append((dir_path, len(os.listdir(root+os.sep+dir_path))))

count_df = pd.DataFrame(category_count, columns=['Classes', 'Total_Images'])
count_df

for name in class_names:
    path = directory_train + "/" + name + "/"
    imagesList = os.listdir(path)
    plt.figure(figsize=(10, 6), constrained_layout=True)
    for i in range(3):
        ax = plt.subplot(3, 3, i + 1)
        img = mpimg.imread(path+imagesList[i])
        plt.imshow(img)
        title = re.sub(r"[_]+","_",name)
        plt.title(title)
        plt.axis("off")

img = mpimg.imread("/content/training_set/training_set/cats/cat.1.jpg")
img.shape

batch_size = 8
IMG_SHAPE = 224

image_gen_train = ImageDataGenerator(rescale=1./255,
                                     rotation_range=45,
                                     width_shift_range=.15,
                                     height_shift_range=.15,
                                     horizontal_flip=True,
                                     zoom_range=0.5
                                    )

train_data_gen = image_gen_train.flow_from_directory(batch_size=batch_size,
                                                     directory=directory_train,
                                                     shuffle=True,
                                                     target_size=(IMG_SHAPE,IMG_SHAPE),
                                                     class_mode='categorical'
)

val_data_gen = image_gen_train.flow_from_directory(batch_size=batch_size,
                                                     directory=directory_validation,
                                                     shuffle=True,
                                                     target_size=(IMG_SHAPE,IMG_SHAPE),
                                                     class_mode='categorical'
)

num_classes = len(class_names)

model = Sequential([
    tf.keras.layers.Conv2D(filters=32, kernel_size=(3, 3), activation='relu', 
                           padding = 'same', input_shape=(IMG_SHAPE,IMG_SHAPE,3)),
    tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=2),
    tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding = 'same'),
    tf.keras.layers.MaxPool2D(pool_size=(2, 2), strides=2),
    
    # Adding dropout to turn down some neurons
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

model.summary()

#tf.keras.utils.plot_model(model, to_file='model.png', show_shapes=True)

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), 
              loss='categorical_crossentropy', 
              metrics=['accuracy'])

epochs = 10

start = perf_counter()
history = model.fit_generator(train_data_gen,
                              steps_per_epoch=int(np.ceil(train_data_gen.n / float(batch_size))),
                              epochs=epochs,
                              validation_data=val_data_gen,
                              validation_steps=int(np.ceil(val_data_gen.n / float(batch_size)))
                             )
end = perf_counter()

print(f"Time taken to execute code : {(end-start)/60}")

model.save("model_cats_dogs.h5")

model = tf.keras.models.load_model('model_cats_dogs.h5')

accuracy_score = model.evaluate(val_data_gen)
print(accuracy_score)
print("Accuracy: {:.4f}%".format(accuracy_score[1] * 100))

print("Loss: ",accuracy_score[0])

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

# plot results
# accuracy
plt.figure(figsize=(10, 16))
plt.rcParams['figure.figsize'] = [16, 9]
plt.rcParams['font.size'] = 14
plt.rcParams['axes.grid'] = True
plt.rcParams['figure.facecolor'] = 'white'
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.ylim([0.43,1.0])
plt.title(f'\nTraining and Validation Accuracy. \nTrain Accuracy: {(str(acc[-1]))} \nValidation Accuracy: {str(val_acc[-1])}')

# loss
plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.title(f'Training and Validation Loss. \nTrain Loss: {str(loss[-1])}\nValidation Loss: {str(val_loss[-1])}')
plt.xlabel('epoch')
plt.tight_layout(pad=3.0)
plt.show()

from keras.preprocessing import image

def load_image(img_path, show=False):

    img = image.load_img(img_path, target_size=(224, 224))
    img_tensor = image.img_to_array(img)                    # (height, width, channels)
    img_tensor = np.expand_dims(img_tensor, axis=0)         # (1, height, width, channels), add a dimension because the model expects this shape: (batch_size, height, width, channels)
    img_tensor /= 255.                                      # imshow expects values in the range [0, 1]

    if show:
        plt.imshow(img_tensor[0])                           
        plt.axis('off')
        plt.show()

    return img_tensor

# image path
## Cat
#img_path = '/content/test_set/test_set/cats/cat.4004.jpg' 

## Dog
img_path = '/content/test_set/test_set/dogs/dog.4004.jpg'     

# load a single image
new_image = load_image(img_path)

# check prediction
pred = model.predict(new_image)

class_names

pred

class_names[np.argmax(pred)]

