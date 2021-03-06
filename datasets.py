
# Note: this file is derived from:
#     https://github.com/guillaume-chevalier/HAR-stacked-residual-bidir-LSTMs
#     (Apache 2.0 License, Copyright 2017, Guillaume Chevalier and Yu Zhao)
# There is also some code derived from:
#     https://github.com/guillaume-chevalier/LSTM-Human-Activity-Recognition
#     (MIT License, Copyright 2017, Guillaume Chevalier)

import os
import pickle
import time

import numpy as np


class Dataset:
    NAME = ""
    SEQUENCE_LENGTH = int()
    INPUT_FEATURES_SIZE = int()
    OUTPUT_CLASSES_SIZE = int()
    LABELS = list()

    def __init__(self, verbose=True, one_hot=False):
        if verbose:
            print("Loading {} dataset...".format(Dataset.NAME))

        self.X_train = None  # [batch_size, sequence_length, features]
        self.X_test = None  # [batch_size], or if one_hot: [batch_size, output_classes_size]
        self.Y_train = None  # (batch_size, sequence_length, features)
        self.Y_test = None  # [batch_size], or if one_hot: [batch_size, output_classes_size]
        self.load_train_test()
        if one_hot:
            self.Y_train = self.one_hot(self.Y_train)
            self.Y_test = self.one_hot(self.Y_test)
        else:
            self.Y_train = np.squeeze(self.Y_train)
            self.Y_test = np.squeeze(self.Y_test)

        if verbose:
            print("Shapes for [self.X_train, self.Y_train, self.X_test, self.Y_test]:")
            for ds in [self.X_train, self.Y_train, self.X_test, self.Y_test]:
                print(
                    "  shape={}".format(ds.shape),
                    ", max-min={}".format(np.max(ds) - np.min(ds)),
                    ", mean={}".format(np.mean(ds)),
                    ", std={}".format(np.std(ds)))
            print("Dataset loaded.\n")

    def one_hot(self, Y_):
        """Function to encode output labels from number indexes.

        e.g.: [[5], [0], [3]] --> [[0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0]]
            argument:   Y_, a 2D np.ndarray containing features by index
            return:     Y_, a 2D np.ndarray containing one-hot features
        """
        Y_ = Y_.reshape(len(Y_))
        return np.eye(self.OUTPUT_CLASSES_SIZE)[np.array(Y_, dtype=np.int32)]  # Returns FLOATS


class UCIHARDataset(Dataset):
    NAME = "UCIHAR"
    SEQUENCE_LENGTH = 128
    INPUT_FEATURES_SIZE = 9
    OUTPUT_CLASSES_SIZE = 6
    LABELS = [
        "WALKING",
        "WALKING_UPSTAIRS",
        "WALKING_DOWNSTAIRS",
        "SITTING",
        "STANDING",
        "LAYING"
    ]

    def __init__(self, verbose=True):
        super().__init__(verbose)

    def load_train_test(self):
        # Those are separate normalised input features for the neural network
        INPUT_SIGNAL_TYPES = [
            "body_acc_x_",
            "body_acc_y_",
            "body_acc_z_",
            "body_gyro_x_",
            "body_gyro_y_",
            "body_gyro_z_",
            "total_acc_x_",
            "total_acc_y_",
            "total_acc_z_"
        ]
        DATA_PATH = "data/"
        DATASET_PATH = DATA_PATH + "UCI HAR Dataset/"

        TRAIN = "train/"
        TEST = "test/"

        X_train_signals_paths = [
            DATASET_PATH + TRAIN + "Inertial Signals/" + signal + "train.txt" for signal in INPUT_SIGNAL_TYPES
        ]
        X_test_signals_paths = [
            DATASET_PATH + TEST + "Inertial Signals/" + signal + "test.txt" for signal in INPUT_SIGNAL_TYPES
        ]
        Y_train_path = DATASET_PATH + TRAIN + "y_train.txt"
        Y_test_path = DATASET_PATH + TEST + "y_test.txt"

        self.X_train = self.load_X(X_train_signals_paths)
        self.X_test = self.load_X(X_test_signals_paths)
        self.Y_train = self.load_Y(Y_train_path)
        self.Y_test = self.load_Y(Y_test_path)


    def load_X(self, X_signals_paths):
        """Load "X" (the neural network's training and testing inputs).

        Given attribute (train or test) of feature, read all 9 features into an
        np ndarray of shape [sample_sequence_idx, time_step, feature_num]
            argument:   X_signals_paths str attribute of feature: 'train' or 'test'
            return:     np ndarray, tensor of features
        """
        X_signals = []

        for signal_type_path in X_signals_paths:
            file = open(signal_type_path, 'r')
            # Read dataset from disk, dealing with text files' syntax
            X_signals.append(
                [np.array(serie, dtype=np.float32) for serie in [
                    row.replace('  ', ' ').strip().split(' ') for row in file
                ]]
            )
            file.close()

        return np.transpose(np.array(X_signals), (1, 2, 0))

    def load_Y(self, y_path):
        """Load "Y" (the neural network's training and testing outputs).

        Read Y file of values to be predicted
            argument: y_path str attibute of Y: 'train' or 'test'
            return: Y ndarray / tensor of the 6 one_hot labels of each sample
        """
        file = open(y_path, 'r')
        # Read dataset from disk, dealing with text file's syntax
        Y_ = np.array(
            [elem for elem in [
                row.replace('  ', ' ').strip().split(' ') for row in file
            ]],
            dtype=np.int32
        )
        file.close()

        # Substract 1 to each output class for friendly 0-based indexing
        return Y_ - 1


class OpportunityDataset(Dataset):
    NAME = "Opportunity"
    SEQUENCE_LENGTH = 24
    INPUT_FEATURES_SIZE = 113
    OUTPUT_CLASSES_SIZE = 18

    def __init__(self, verbose=True):
        super().__init__(verbose)

    def load_train_test(self):
        raise NotImplementedError()

    def load_dataset(self, filename):
        raise NotImplementedError()
