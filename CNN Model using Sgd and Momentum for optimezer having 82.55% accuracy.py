#import the necceasry library as shown by Dr.Venga
import tensorflow as tf
from tensorflow.keras import layers,models, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import numpy as np

#Check if a GPU is used as my laptop had some issue
print("Num GPUs Available: " , len(tf.config.list_physical_devices('GPU')))

# Data Preparation-Cifar-10 data
print("Loading CIFAR-10 data...")
#CIFAR-10 contain 60,000 32 x 32 color images in 10 classes
cifar10 = tf.keras.datasets.cifar10
(train_images,train_labels),(test_images,test_labels) = cifar10.load_data()
#Images comes as integers from (0-255)
#Dividing by 255 scales them to a range of 0.0 to 1.0 as NN perform better in normalized input values
train_images,test_images = train_images/255.0, test_images/255.0

# Class name for the 10 categories in CIFAR-10
class_names = [ 'airplane','automobile', 'bird','cat','deer','dog', 'frog','horse','ship','truck']
#Cnn expect a 4D tensor:( Batch_Size, Height, Width(reshape the 28x28 images), Channels which will be 1 as MNIST is greyscale)
#train_images = train_images.reshape((60000,28,28,1)) # no need for now
#test_images = test_images.reshape((10000,28,28,1)) # no need for now

#Data Augmentation
# Adding some random flip, rotation and zoom to improve the way the model seeing the image.( Change of prespective and perceptive)
data_augmentation = tf.keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
])



#2.Model Architecture

model =models.Sequential([
    #change to 32 x32 with 3 channels(RGB)
    Input(shape=(32,32,3)),

    #Apply data augmentation
    data_augmentation,

    #Block 1
    #This block have 32 filters that looks for simple things like vertical/horizontal line/edges and basic colours
    layers.Conv2D(32,(3,3),padding ='same',activation ='relu'), 
    layers.BatchNormalization(), #data trimming so no extreme value which make the learning faster and stable
    layers.Conv2D(32,(3,3), activation = 'relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)), # make the model faster and felxible by shrinking the image size
    layers.Dropout(0.2), #Prevent overfitting

    #Block 2
    #This block have 64 filters which will combine block 1 to start seeing shapes and textures if any
    layers.Conv2D(64,(3,3),padding ='same',activation ='relu'), 
    layers.BatchNormalization(), #data trimming so no extreme value which make the learning faster and stable
    layers.Conv2D(64,(3,3), activation = 'relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)), # make the model faster and felxible by shrinking the image size
    layers.Dropout(0.3), #Prevent overfitting

    #Block 3
    #This block have 128 filters which will combine block 1 and 2 to start seeing complex strutures like wings, wheel or beaks
    layers.Conv2D(128,(3,3),padding ='same',activation ='relu'), 
    layers.BatchNormalization(), #data trimming so no extreme value which make the learning faster and stable
    layers.Conv2D(128,(3,3), activation = 'relu'),
    layers.BatchNormalization(),
    layers.MaxPooling2D((2,2)), # make the model faster and felxible by shrinking the image size
    layers.Dropout(0.4), #Prevent overfitting
    
    #Final Classification layers
    # 1. Flatten to ocnverts the 2D features into a list of numbers
    layers.Flatten(),
    #Thinking layers
    layers.Dense(128,activation ='relu'),
    #data trimming
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(10,activation = 'softmax'),
    
    
])

#Compilation
# usin adam as optimizer that automatically djust the learning rate
#loss where measures how wrng the model is using SparseCategorical is used for integer
#metric to track accuracy
opt_sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9)

model.compile(optimizer = opt_sgd,
              loss ='sparse_categorical_crossentropy',
              metrics=['accuracy'])

#print table showing the layers and number of trainable parameters
model.summary()

#Trying out Best Epoch Logic where it will compare the previous and present value and take the best value
# callback monitors val_accuracy and compares it to previous epochs
early_stop = EarlyStopping(
    monitor ='val_accuracy',
    patience=12,
    restore_best_weights = True, # this reload the best weight automatically
    verbose =1,
)

#This compares and saves only if the current epoch is better than previous best
checkpoint = ModelCheckpoint(
    'cifar10_model_v2_best.keras',
    monitor = 'val_accuracy',
    save_best_only = True,
    verbose = 1
)




#Training
#epochs = 60: The model looks at the entire dataset 60times as color images are more complex than digits
# 
print("\n Startng training with optimzer:{model.optimizer.__.class__.__name__}(Momentum=0.9)")
history = model.fit(
                    train_images, train_labels,
                    epochs = 60,
                    validation_data = (test_images,test_labels),
                    batch_size = 64,
                    callbacks = [ early_stop,checkpoint]
            )

#Integration part where the model is saved
#saved file later moved to Webots controller folder
model.save('Final_cifar10_model.keras')
print("\n Model saved as 'Final_cifar10_model.keras' saved sucessfully")

#Evaluation and Summary
val_acc_history = history.history['val_accuracy']
best_epoch = np.argmax(val_acc_history) +1
best_val_acc = val_acc_history[best_epoch -1]

print("\n" + "="*30)
print(f"TRAINING SUMMARY")
print(f"Best Epoch Found: {best_epoch}")
print(f"Highest Val Accuracy achieved: {best_val_acc*100:.2f}%")
print(f"Model state restored to Best Epoch ({best_epoch}) weights.")
print("="*30)

test_loss,test_acc = model.evaluate(test_images, test_labels,verbose = 2)
print(f'\n Final Accuracy on Test Data:{test_acc*100:.2f}%')

#Prediction
#model.predict return an array of 10 possibilities for the image
prediction = model.predict(test_images[:1])
#argmax() piks the index(0-9) with the highest probability.
print(f"Model Prediction: {prediction.argmax()}")
print(f"Actual Label:{test_labels[0]}")