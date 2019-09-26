"""
Adapted from http://iryndin.net/post/xgboost_for_iris_dataset/
"""
import os

import cv2
import numpy as np
import xgboost
from imutils import paths
from sklearn import metrics
from sklearn.model_selection import train_test_split

from helpers import resize_to_fit

LETTER_IMAGES_FOLDER = "extracted_letter_images"


def load_data():
    # initialize the data and labels
    data = []
    labels = []

    # loop over the input images
    for image_file in paths.list_images(LETTER_IMAGES_FOLDER):
        # Load the image and convert it to grayscale
        image = cv2.imread(image_file)

        if type(image) == type(None):
            print(f"{image_file} returned None from cv2.imread")
            os.remove(image_file)
            continue

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Resize the letter so it fits in a 20x20 pixel box
        image = resize_to_fit(image, 20, 20)

        # Add a third channel dimension to the image to make Keras happy
        image = np.expand_dims(image, axis=2)

        # Grab the name of the letter based on the folder it was in
        label = image_file.split(os.path.sep)[-2]

        # Add the letter image and it's label to our training data
        data.append(image)
        labels.append(label)

    # scale the raw pixel intensities to the range [0, 1] (this improves training)
    data = np.array(data, dtype="float") / 255.0
    labels = np.array(labels)

    n_samples = len(data)
    data = data.reshape((n_samples, -1))

    # .squeeze() to remove unwanted dimension https://stackoverflow.com/a/25453912/5140672
    return data.squeeze(), labels


if __name__ == "__main__":
    images, labels = load_data()

    # split into test and training
    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

    # convert numpy arrays into special DMatrix
    # https://xgboost.readthedocs.io/en/latest/python/python_api.html#xgboost.DMatrix
    training_set = xgboost.DMatrix(X_train, label=y_train)
    testing_set = xgboost.DMatrix(X_test, label=y_test)

    param = {
        'max_depth': 3,  # the maximum depth of each tree
        'eta': 0.3,  # the training step for each iteration
        'silent': 0,  # logging mode - quiet
        'objective': 'multi:softmax',  # multiclass classification using the softmax objective
        'num_class': 10  # the number of classes that exist in this dataset
    }
    num_round = 20  # the number of training iterations

    # train and dump the model to a .txt file
    model = xgboost.train(param, training_set, num_round)
    model.dump_model('xgboostmodel.txt')

    # check the accuracy on the test set
    predictions = model.predict(testing_set)
    acc = metrics.accuracy_score(y_test.astype(int), predictions.astype(int))
    print(acc)
