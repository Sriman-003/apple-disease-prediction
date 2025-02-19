# -*- coding: utf-8 -*-
"""sriman k.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Lf-FYMOhPJv_oHIasuhHsimREbNo2n5t
"""


import os
import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive, files
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dropout, Dense
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.utils import load_img, img_to_array
from sklearn.metrics import classification_report, confusion_matrix

# Mount Google Drive
drive.mount('/content/drive')

# Directories
TRAINING_DIR = "/content/drive/MyDrive/apple dataset/Train"
TEST_DIR = "/content/drive/MyDrive/apple dataset/Test"
BATCH_SIZE = 64
IMAGE_SIZE = (224, 224)

# Display sample data count
for folder in os.listdir(TRAINING_DIR):
    files = len(os.listdir(os.path.join(TRAINING_DIR, folder)))
    print(f'Training data - {folder}: {files} images')
for folder in os.listdir(TEST_DIR):
    files = len(os.listdir(os.path.join(TEST_DIR, folder)))
    print(f'Testing data - {folder}: {files} images')

# View random image
def view_random_image(target_dir, target_class):
    target_folder = os.path.join(target_dir, target_class)
    random_image = random.choice(os.listdir(target_folder))
    img_path = os.path.join(target_folder, random_image)
    img = load_img(img_path)
    plt.imshow(img)
    plt.title(target_class)
    plt.axis('off')
    print(f"Image shape: {img.size}")
    return img

# Define class_names outside the function
class_names = ['Blotch_Apple', 'Normal_Apple', 'Rot_Apple', 'Scab_Apple']

plt.figure(figsize=(20, 10))
for i in range(12):
    plt.subplot(3, 4, i + 1)
    class_name = random.choice(class_names)
    view_random_image(TRAINING_DIR, class_name)

# Data Generators
def train_val_generators(training_dir, testing_dir):
    train_datagen = ImageDataGenerator(rescale=1.0 / 255.0,
                                       rotation_range=45,
                                       width_shift_range=0.2,
                                       height_shift_range=0.2,
                                       shear_range=0.2,
                                       zoom_range=0.2,
                                       horizontal_flip=True,
                                       fill_mode='nearest')
    train_generator = train_datagen.flow_from_directory(directory=training_dir,
                                                        target_size=IMAGE_SIZE,
                                                        batch_size=BATCH_SIZE,
                                                        class_mode='categorical')

    validation_datagen = ImageDataGenerator(rescale=1.0 / 255.0)
    validation_generator = validation_datagen.flow_from_directory(directory=testing_dir,
                                                                  target_size=IMAGE_SIZE,
                                                                  batch_size=BATCH_SIZE,
                                                                  class_mode='categorical')
    return train_generator, validation_generator

train_generator, validation_generator = train_val_generators(TRAINING_DIR, TEST_DIR)

# Model with Transfer Learning
base_model = MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dropout(0.5),
    Dense(4, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

train_datagen = ImageDataGenerator(
    rescale=1.0 / 255.0,
    rotation_range=90,  # Increased rotation range
    width_shift_range=0.3,  # Increased width shift range
    height_shift_range=0.3,  # Increased height shift range
    shear_range=0.3,  # Increased shear range
    zoom_range=0.3,  # Increased zoom range
    brightness_range=[0.8, 1.2],  # Added brightness variation
    horizontal_flip=True,
    fill_mode='nearest'
)

# Callbacks
checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True, verbose=1)  # Change file extension to .h5
early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True, verbose=1)

history = model.fit(train_generator,
                    validation_data=validation_generator,
                    epochs=15,
                    steps_per_epoch=len(train_generator),
                    validation_steps=len(validation_generator),
                    callbacks=[checkpoint, early_stopping])

# Plot Results
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']

# Fix: Use the length of the shorter array (val_acc or val_loss) for epochs
epochs = range(len(val_acc))  # or epochs = range(len(val_loss))

plt.figure(figsize=(12, 6))
plt.plot(epochs, acc[:len(val_acc)], label='Training Accuracy') # Slice acc to match val_acc length
plt.plot(epochs, val_acc, label='Validation Accuracy')
plt.title('Accuracy')
plt.legend()
plt.show()

plt.figure(figsize=(12, 6))
plt.plot(epochs, loss[:len(val_loss)], label='Training Loss') # Slice loss to match val_loss length
plt.plot(epochs, val_loss, label='Validation Loss')
plt.title('Loss')
plt.legend()
plt.show()

# Evaluate Model
predictions = model.predict(validation_generator)
y_pred = np.argmax(predictions, axis=1)
print(classification_report(validation_generator.classes, y_pred, target_names=class_names))

cm = confusion_matrix(validation_generator.classes, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.title('Confusion Matrix')
plt.show()

from google.colab import files #Explicitly reimport files from google.colab to recover the module you want

uploaded = files.upload() #Now this should work correctly.
class_names = ['Blotch_Apple', 'Normal_Apple', 'Rot_Apple', 'Scab_Apple']  # Define class names



for fn in uploaded.keys():
    img_path = fn
    img = load_img(img_path, target_size=(224, 224))  # Load and resize image
    x = img_to_array(img) / 255.0  # Preprocess image
    x = np.expand_dims(x, axis=0)  # Add batch dimension

    prediction = model.predict(x)  # Make prediction
    predicted_index = np.argmax(prediction)  # Get predicted class index
    predicted_class = class_names[predicted_index]  # Get predicted class name

    # Print prediction result
    print(f"Prediction: {predicted_class}")
    print(f"Probabilities: {prediction[0]}")  # Print probabilities for each class

    # Display prediction image
    plt.imshow(img)
    plt.title(f"Prediction: {predicted_class}")
    plt.axis('off')
    plt.show()
