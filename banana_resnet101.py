# -*- coding: utf-8 -*-
"""banana_resnet101.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YshUxJSZqbR5rL3xBHW1kp8UAA_Xr0hv
"""

from google.colab import drive
drive.mount('/content/drive')

#!/usr/bin/env python
# coding: utf-8

# In[6]:


import tensorflow as tf
import pandas as pd
import numpy as np

from tensorflow.keras import models, layers
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import *
from keras.layers import Bidirectional, LSTM
from tensorflow.keras.preprocessing import image_dataset_from_directory
import os
from keras.applications.resnet import ResNet101
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping


# In[7]:


channels = 3
EPOCHS = 30
IMAGE_SIZE = (256, 256)
normalizationVal = 255.0
classes = list()
for root, dirs, files in os.walk('/content/drive/MyDrive/banana_dataset/Test'):
    for name in dirs:
        classes.append(name)
print(classes)
directory_list = classes


# In[8]:


train_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory = '/content/drive/MyDrive/banana_dataset/Train',
    label_mode = "categorical",
    class_names = directory_list,
    image_size= IMAGE_SIZE,
    batch_size= 32,
    seed= 42,
    validation_split = 0.2,
    subset = "training",
    color_mode = "rgb"
    
    
)


# In[9]:


val_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory = '/content/drive/MyDrive/banana_dataset/Train',
    label_mode = "categorical",
    class_names = directory_list,
    image_size= IMAGE_SIZE,
    batch_size= 32,
    seed= 42,
    validation_split = 0.2,
    subset = "validation",
    color_mode = "rgb"
 )


# In[11]:


test_ds = tf.keras.preprocessing.image_dataset_from_directory(
    directory = '/content/drive/MyDrive/banana_dataset/Test',
    label_mode = 'categorical',
    class_names = directory_list,
    image_size= IMAGE_SIZE,
    batch_size= 1,
    seed= 42,
   
    color_mode = "rgb"
    
)


# In[8]:


# print(train_label)


# In[12]:


# plt.figure(figsize =(10,10))

# for image_batch, label_batch in train_ds.take(1):
#     for i in range(12):
#         ax = plt.subplot(3,4,i+1)
#         plt.imshow(image_batch[i].numpy().astype("uint8"))
#         plt.title(directory_list[np.argmax(label_batch[i])])
#         plt.axis("off")


# In[ ]:





# In[ ]:





# In[13]:


len(train_ds)


# In[14]:


len(val_ds)


# In[15]:


len(test_ds)


# In[16]:


train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)
val_ds = val_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)
test_ds = test_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)


# In[ ]:





# In[17]:


from keras import backend as K
def recall_m(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true*y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives/ (possible_positives +K.epsilon())
    return recall
                        
                           


# In[18]:


def precision_m(y_true , y_pred):
    true_positives = K.sum(K.round(K.clip(y_true*y_pred ,0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives/ (predicted_positives+ K.epsilon())
    return precision


# In[19]:


def f1_m(y_true, y_pred):
    precision = precision_m(y_true, y_pred)
    recall = recall_m(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))


# In[ ]:





# In[20]:


resnet = ResNet101(input_shape = (256, 256, 3), weights = 'imagenet', include_top = False)


# In[23]:


for layer in resnet.layers:
    layer.trainable = False


# In[24]:


x = Flatten()(resnet.output)


# In[25]:


prediction = Dense(len(classes), activation = 'softmax')(x)


# In[26]:


model = tf.keras.Model(inputs= resnet.input, outputs= prediction)


# In[27]:


model.summary()


# In[28]:


model.compile(
    loss = 'categorical_crossentropy',
    optimizer = 'adam',
    metrics=['accuracy', recall_m, precision_m, f1_m]
)


# In[ ]:





# In[29]:

history = model.fit(
    train_ds,
    epochs = EPOCHS,
    batch_size = 32,
    verbose = 1,
    validation_data = val_ds,
 
)


# In[ ]:


EPOCHS = len(history.history['loss']) 


# In[37]:


print(model.evaluate(test_ds))


# In[38]:


acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']


# In[39]:


plt.figure(figsize =(16,8))
plt.subplot(1,2,1)
plt.plot(range(EPOCHS), acc , label='Training Accuracy')
plt.plot(range(EPOCHS), val_acc , label ='Validation Accuracy')
plt.legend(loc ='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1,2,2)
plt.plot(range(EPOCHS ), loss, label ='Training losss')
plt.plot(range(EPOCHS), val_loss , label ='Validation loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.savefig('banana_resnet101_model.png')


# In[ ]:





# In[43]:


import numpy as np
for images_batch, labels_batch in test_ds.take(1):
    first_image = images_batch[0].numpy().astype('uint8')
    first_label = labels_batch[0].numpy()
    #print(first_label)
    print("first image to predict")
    plt.imshow(first_image)
    print("actual lable:", directory_list[np.argmax(first_label)])
    
    batch_prediction = model.predict(images_batch)
    predict_class =  directory_list[np.argmax(batch_prediction)]
    
    print("Predicted lable :",predict_class)
   


# In[44]:


predicted_batch = model.predict(val_ds)
predicted_id = np.argmax(predicted_batch, axis =-1)
# print(predicted_id)
predicted_label_batch = directory_list[predicted_id[0]]
print(predicted_label_batch)


# In[45]:


model.save('banana_resnet101_model.h5')