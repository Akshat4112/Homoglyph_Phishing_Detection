from matplotlib import pyplot
from keras.utils import to_categorical
from keras import optimizers
from keras import layers
from keras import models
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.python.client import device_lib
import tensorflow.keras.backend as K
import wandb
from wandb.keras import WandbCallback
import argparse
import os
from datetime import datetime
from tensorflow.keras.layers import GlobalAveragePooling2D, GlobalMaxPooling2D, Reshape, Dense, multiply, Permute, Concatenate, Conv2D, Add, Activation, Lambda
from attentionModule import attach_attention_module

class NeuralNetwork:
  def __init__(self) -> None:
    wandb.init(project="HomoglyphDetection", entity="robofied")
    print(device_lib.list_local_devices())
    # print(K._get_available_gpus())
    pass

  def DataGenerator(self, train_dir, valid_dir):
    self.train_dir = train_dir
    self.valid_dir = valid_dir

    # create data generator
    datagen = ImageDataGenerator(rescale=1./255)

    # prepare iterator
    print("Before datagen..")
    self.train_it = datagen.flow_from_directory(train_dir,class_mode='binary', batch_size=1, target_size=(256, 256))
    print("Datagen completed..")
    self.validation_it = datagen.flow_from_directory(valid_dir,class_mode='binary', batch_size=1, target_size=(256, 256))
    
  def SimpleCNN(self, activation=1, attention_module=1):

    wandb.config = {"learning_rate": 1e-4,
                    "epochs": 30,
                    "batch_size": 1}

    model = models.Sequential()
    model.add(layers.Conv2D(32, (5, 5), activation='relu', input_shape=(256, 256, 3)))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    # attention_module
    if attention_module is not None:
        up = attach_attention_module(model, attention_module)

    x = Lambda(lambda inputs, scale: inputs[0] + inputs[1] * scale, output_shape=K.int_shape(x)[1:], arguments={'scale': 8}, name='block_name')([x, up])
    if activation is not None:
        x = Activation(activation, name='block_name' + '_ac')(x)
    model.compile(loss='binary_crossentropy',
                  optimizer=optimizers.RMSprop(lr=1e-4),
                  metrics=['acc'])

    print("Training Starting..")
    model.fit(self.train_it,validation_data=self.validation_it, steps_per_epoch=500, epochs=30, verbose=1, callbacks=[WandbCallback()])
    print("Training Completed..")
    
    # save model
    name = '../models/modelSimpleCNN' + str(datetime.now()) + '.h5'
    model.save(name)

  def AttentionCNN(self):

    model = models.Sequential()
    model.add(layers.Conv2D(32, (5, 5), activation='relu', input_shape=(256, 256, 3)))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.BatchNormalization())
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPool2D(2, 2))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))

    
    model.compile(loss='binary_crossentropy',
                  optimizer=optimizers.RMSprop(lr=1e-4),
                  metrics=['acc'])

    print("Training Starting..")
    model.fit(self.train_it,validation_data=self.validation_it, steps_per_epoch=500, epochs=30, verbose=1, callbacks=[WandbCallback()])
    print("Training Completed..")
    
    # save model
    name = '../models/modelAttentionCNN' + str(datetime.now()) + '.h5'
    model.save(name)

    return None

  # def Evaluation():
  #       # fit model

  #   print("Evalutaing model..")

  #   # prepare iterator
  #   print("Before datagen..")
  #   test_dir = os.path.join(path_arg, "final_test")
  #   test_it = datagen.flow_from_directory(test_dir, class_mode='binary', batch_size=1, target_size=(256, 256))
  #   print("Datagen completed..")

  #   # evaluate model
  #   print("Evaluating Model..")

  #   _, acc, f1_score, precision, recall = model.evaluate_generator(test_it, steps=500, verbose=0)
  #   print('> %.3f' % (acc * 100.0))

  #   print("Computing Precision and Recall for Classification.")

  #   return None

obj = NeuralNetwork()
obj.DataGenerator('../data/train', '../data/valid')
print("Data Generation Completed")
obj.SimpleCNN()