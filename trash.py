import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import matplotlib.pyplot as plt
import cv2
import pywt
import time
import PIL.Image as Image
import tensorflow_hub as hub
import datetime

path_to_train = r"C:/Users/mish/Downloads/trash/GARBAGE CLASSIFICATION/dataset/train"
import os
img_names = []
for entry in os.scandir(path_to_train):
    if entry.is_dir():
        img_names.append(entry.path)
img_PathToType = {}
for img_individual in img_names:
    file_list = []
    object_type = img_individual.split('/')[-1]
    object_type = object_type.split('_')[0]
    for entry in os.scandir(img_individual):
        file_list.append(entry.path)
    img_PathToType[object_type] = file_list 
(img_PathToType)
# Создание словаря категорий объектов
object_category_dict = {}
count = 0

for img in img_names:   
    # Извлекаем имя файла
    object_type = img.split('/')[-1]  
    object_type = object_type.split('_')[0]  # Получаем тип объекта

    # Убираем 'train' из названия типа объекта
    if object_type.startswith('train'):
        object_type = object_type[len('train'):].lstrip('_')

    # Убираем любые начальные обратные слэши
    object_type = object_type.lstrip('\\')

    # Добавляем тип объекта в словарь, только если он еще не существует
    if object_type not in object_category_dict:
        object_category_dict[object_type] = count
        count += 1

# Вывод результата
print("Содержимое object_category_dict:", object_category_dict)
X, y = [], []
for object_names, training_files in img_PathToType.items():
    for training_image in training_files:
        img = cv2.imread(training_image)
        
        # Получаем имя объекта без префикса
        object_name_key = object_names.split('\\')[-1].lstrip('train_')

        # Проверка наличия ключа
        if object_name_key in object_category_dict:
            X.append(img)
            y.append(object_category_dict[object_name_key])  # Добавление метки
        else:
            print(f"Ключ '{object_name_key}' не найден в object_category_dict. Текущие ключи: {list(object_category_dict.keys())}")

# Проверка размеров
print(f"Количество изображений в X: {len(X)}")
print(f"Количество меток в y: {len(y)}")
y = np.array(y)
y.shape
plt.imshow(X[1900])
y[1900]
X = np.array(X).reshape(len(X),384,512,3)
X.shape
path_to_test = r"C:/Users/mish/Downloads/trash/GARBAGE CLASSIFICATION/dataset/test"
import os
img_names_test = []
for entry in os.scandir(path_to_test):
    if entry.is_dir():
        img_names_test.append(entry.path)
img_names_test
img_PathToTypeTest = {}

for img_individual in img_names_test:
    file_list_test = []
    
    # Получаем имя типа объекта, убирая префикс 'test\\'
    object_type = img_individual.split('\\')[-1]  # Если используете Windows, разделитель - '\\'
    object_type = object_type.split('_')[0]  # Извлекаем тип объекта
    print(object_type)  # Проверка значения object_type
    
    # Проверяем, существует ли директория
    if os.path.isdir(img_individual):
        for entry in os.scandir(img_individual):
            file_list_test.append(entry.path)
    
    # Сохраняем в словарь без префикса 'test\\'
    img_PathToTypeTest[object_type] = file_list_test 

# Вывод содержимого img_PathToTypeTest без 'test\\'
print("Содержимое img_PathToTypeTest без 'test\\':")
for object_type, files in img_PathToTypeTest.items():
    print(f"{object_type}: {files}")

# Инициализация списков для тестовых данных
X_test, y_test = [], []

# Извлекаем изображения и метки
for object_names, training_files in img_PathToTypeTest.items():
    # Извлекаем тип объекта без 'test\\' для использования в словаре
    object_name_key = object_names.split('\\')[-1]
    
    # Проверяем, есть ли такой ключ в словаре меток
    if object_name_key in object_category_dict:
        for training_image in training_files:
            img = cv2.imread(training_image)

            if img is not None:  # Проверяем, что изображение успешно загружено
                X_test.append(img)
                y_test.append(object_category_dict[object_name_key])  # Теперь это будет корректный ключ

# Проверка, есть ли изображения
if len(X_test) > 500 and len(y_test) > 500:
    plt.imshow(cv2.cvtColor(X_test[500], cv2.COLOR_BGR2RGB))  # Конвертируем BGR в RGB для отображения
    print("Метка изображения:", y_test[500])
else:
    print(f"Недостаточно изображений. В X_test: {len(X_test)}, в y_test: {len(y_test)}")
X_test = np.array(X_test).reshape(len(X_test),384,512,3)
print(X_test.shape)
y_test = np.array(y_test)
print(y_test.shape)
train_generator = ImageDataGenerator(
    rescale = 1./255,  # normalization of images
    rotation_range = 40, # augmention of images to avoid overfitting
    shear_range = 0.2,
    zoom_range = 0.2,
    fill_mode = 'nearest'
)

val_generator = ImageDataGenerator(rescale = 1./255)

train_iterator = train_generator.flow(X, y, batch_size=512, shuffle=True)

val_iterator = val_generator.flow(X_test, y_test, batch_size=512, shuffle=False)
model = Sequential()
# add the pretrained model
model.add(ResNet50(include_top=False, pooling='avg', weights='imagenet'))
# add fully connected layer with output
model.add(Dense(512, activation='relu'))
model.add(Dense(6, activation='softmax'))

# set resnet layers not trainable
model.layers[0].trainable=False
model.summary()
model.compile(optimizer='Adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X,y, epochs=10)
model.evaluate(X_test,y_test)
model.save('model.h5')
