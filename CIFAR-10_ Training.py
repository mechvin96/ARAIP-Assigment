#import the necceasry library as shown by Dr.Venga
import tensorflow as tf
from tensorflow.keras import layers,models, Input
import matplotlib.pyplot as plt

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

#2.Model Architecture

model =models.Sequential([
    #tell the model the shape first follow by adding the eye Conv2D with the size use relu to turn off negative signal to make the learning faster
    #follow by Downsampling
    #change to 32 x32 with 3 channels(RGB)
    Input(shape=(32,32,3)),
    #first conv block
    layers.Conv2D(32,(3,3),activation ='relu'), #features to look for using 32 filter(basic) 
    layers.MaxPooling2D((2,2)),
    #second conv block
    layers.Conv2D(64,(3,3),activation ='relu'), #features to look for using 64 filter(complex) 
    layers.MaxPooling2D((2,2)),

    # third conv block( adding for more complex color features)
    layers.Conv2D(64,(3,3),activation ='relu'),

    # 1. Flatten to ocnverts the 2D features into a list of numbers
    #2. Dense: A standard nnl where every neuron connects to every others 
    # Convolutions is used to try reasoning the features of 64 neurons
    layers.Flatten(),
    layers.Dense(64,activation ='relu'),
    #Final Dense layer: 10 neuron correspond to dgit 0 through 9.
    # Using softmax to convert outputs into probabilties
    layers.Dense(10,activation = 'softmax')  
    
    
])

#Compilation
# usin adam as optimizer that automatically djust the learning rate
#loss where measures how wrng the model is using SparseCategorical is used for integer
#metric to track accuracy

model.compile(optimizer ='adam',
              loss ='sparse_categorical_crossentropy',
              metrics=['accuracy'])

#print table showing the layers and number of trainable parameters
model.summary()

#Training
#epochs = 10: The model looks at the entire dataset 1otimes as color images are more complex than digits
# 
print("\n Startng training(make take longer than MNIST....")
history = model.fit(train_images, train_labels, epochs = 20,validation_data = (test_images,test_labels)) #try doubling the epoch to see if the improve the accuracy

#Integration part where the model is saved
#saved file later moved to Webots controller folder
model.save('cifar10_model.keras')
print("\n Model saved as 'cifar10_model.keras'")

#Evaluation
#Test the model on the 10,000 imgs it has never seen before
test_loss,test_acc = model.evaluate(test_images, test_labels,verbose = 2)
print(f'\n Final Accuracy on Test Data:{test_acc*100:.2f}%')

#Prediction
#model.predict return an array of 10 possibilities for the image
prediction = model.predict(test_images[:1])
#argmax() piks the index(0-9) with the highest probability.
print(f"Model Prediction: {prediction.argmax()}")
print(f"Actual Label:{test_labels[0]}")
