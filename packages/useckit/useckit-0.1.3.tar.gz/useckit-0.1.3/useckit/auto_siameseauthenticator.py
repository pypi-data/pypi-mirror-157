# https://keras.io/examples/vision/siamese_contrastive/

import random
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt


class AutoSiameseAuthenticator(object):
    epochs = 10
    batch_size = 16
    margin = 1  # Margin for constrastive loss.

    def __init__(self,
                 x_train: np.ndarray,  # training data (mandatory)
                 y_train: np.ndarray,  # training labels (mandatory)
                 x_val: np.ndarray,  # validation data (mandatory)
                 y_val: np.ndarray,  # validation labels (mandatory)
                 ):
        self.x_train = x_train
        self.y_train = y_train
        self.x_val = x_val
        self.y_val = y_val

    def loss(self, margin=1):
        """Provides 'constrastive_loss' an enclosing scope with variable 'margin'.

      Arguments:
          margin: Integer, defines the baseline for distance for which pairs
                  should be classified as dissimilar. - (default is 1).

      Returns:
          'constrastive_loss' function with data ('margin') attached.
      """

        # Contrastive loss = mean( (1-true_value) * square(prediction) +
        #                         true_value * square( max(margin-prediction, 0) ))
        def contrastive_loss(y_true, y_pred):
            """Calculates the constrastive loss.

          Arguments:
              y_true: List of labels, each label is of type float32.
              y_pred: List of predictions of same length as of y_true,
                      each label is of type float32.

          Returns:
              A tensor containing constrastive loss as floating point value.
          """

            square_pred = tf.math.square(y_pred)
            margin_square = tf.math.square(tf.math.maximum(margin - (y_pred), 0))
            return tf.math.reduce_mean(
                (1 - y_true) * square_pred + (y_true) * margin_square
            )

        return contrastive_loss

    def make_pairs(self, x, y):
        """Creates a tuple containing image pairs with corresponding label.

        Arguments:
            x: List containing images, each index in this list corresponds to one image.
            y: List containing labels, each label with datatype of `int`.

        Returns:
            Tuple containing two numpy arrays as (pairs_of_samples, labels),
            where pairs_of_samples' shape is (2len(x), 2,n_features_dims) and
            labels are a binary array of shape (2len(x)).
        """

        num_classes = max(y) + 1
        digit_indices = [np.where(y == i)[0] for i in range(num_classes)]

        pairs = []
        labels = []

        for idx1 in range(len(x)):
            # add a matching example
            x1 = x[idx1]
            label1 = y[idx1]
            idx2 = random.choice(digit_indices[label1])
            x2 = x[idx2]

            pairs += [[x1, x2]]
            labels += [1]

            # add a non-matching example
            label2 = random.randint(0, num_classes - 1)
            while label2 == label1:
                label2 = random.randint(0, num_classes - 1)

            idx2 = random.choice(digit_indices[label2])
            x2 = x[idx2]

            pairs += [[x1, x2]]
            labels += [0]

        return np.array(pairs), np.array(labels).astype("float32")

    def visualize(self, pairs, labels, to_show=6, num_col=3, predictions=None, test=False):
        """Creates a plot of pairs and labels, and prediction if it's test dataset.

        Arguments:
            pairs: Numpy Array, of pairs to visualize, having shape
                   (Number of pairs, 2, 28, 28).
            to_show: Int, number of examples to visualize (default is 6)
                    `to_show` must be an integral multiple of `num_col`.
                     Otherwise it will be trimmed if it is greater than num_col,
                     and incremented if if it is less then num_col.
            num_col: Int, number of images in one row - (default is 3)
                     For test and train respectively, it should not exceed 3 and 7.
            predictions: Numpy Array of predictions with shape (to_show, 1) -
                         (default is None)
                         Must be passed when test=True.
            test: Boolean telling whether the dataset being visualized is
                  train dataset or test dataset - (default False).

        Returns:
            None.
        """

        # Define num_row
        # If to_show % num_col != 0
        #    trim to_show,
        #       to trim to_show limit num_row to the point where
        #       to_show % num_col == 0
        #
        # If to_show//num_col == 0
        #    then it means num_col is greater then to_show
        #    increment to_show
        #       to increment to_show set num_row to 1
        num_row = to_show // num_col if to_show // num_col != 0 else 1

        # `to_show` must be an integral multiple of `num_col`
        #  we found num_row and we have num_col
        #  to increment or decrement to_show
        #  to make it integral multiple of `num_col`
        #  simply set it equal to num_row * num_col
        to_show = num_row * num_col

        # Plot the images
        fig, axes = plt.subplots(num_row, num_col, figsize=(5, 5))
        for i in range(to_show):

            # If the number of rows is 1, the axes array is one-dimensional
            if num_row == 1:
                ax = axes[i % num_col]
            else:
                ax = axes[i // num_col, i % num_col]

            ax.imshow(tf.concat([pairs[i][0], pairs[i][1]], axis=1), cmap="gray")
            ax.set_axis_off()
            if test:
                ax.set_title("True: {} | Pred: {:.5f}".format(labels[i], predictions[i][0]))
            else:
                ax.set_title("Label: {}".format(labels[i]))
        if test:
            plt.tight_layout(rect=(0, 0, 1.9, 1.9), w_pad=0.0)
        else:
            plt.tight_layout(rect=(0, 0, 1.5, 1.5))
        plt.show()

    # Provided two tensors t1 and t2
    # Euclidean distance = sqrt(sum(square(t1-t2)))
    def euclidean_distance(self, vects):
        """Find the Euclidean distance between two vectors.

        Arguments:
            vects: List containing two tensors of same length.

        Returns:
            Tensor containing euclidean distance
            (as floating point value) between vectors.
        """

        x, y = vects
        sum_square = tf.math.reduce_sum(tf.math.square(x - y), axis=1, keepdims=True)
        return tf.math.sqrt(tf.math.maximum(sum_square, tf.keras.backend.epsilon()))

    def create_model(self):
        input = layers.Input((28, 28, 1))
        x = tf.keras.layers.BatchNormalization()(input)
        x = layers.Conv2D(4, (5, 5), activation="tanh")(x)
        x = layers.AveragePooling2D(pool_size=(2, 2))(x)
        x = layers.Conv2D(16, (5, 5), activation="tanh")(x)
        x = layers.AveragePooling2D(pool_size=(2, 2))(x)
        x = layers.Flatten()(x)

        x = tf.keras.layers.BatchNormalization()(x)
        x = layers.Dense(10, activation="tanh")(x)
        embedding_network = keras.Model(input, x)

        input_1 = layers.Input((28, 28, 1))
        input_2 = layers.Input((28, 28, 1))

        # As mentioned above, Siamese Network share weights between
        # tower networks (sister networks). To allow this, we will use
        # same embedding network for both tower networks.
        tower_1 = embedding_network(input_1)
        tower_2 = embedding_network(input_2)

        merge_layer = layers.Lambda(self.euclidean_distance)([tower_1, tower_2])
        normal_layer = tf.keras.layers.BatchNormalization()(merge_layer)
        output_layer = layers.Dense(1, activation="sigmoid")(normal_layer)
        siamese = keras.Model(inputs=[input_1, input_2], outputs=output_layer)

        return siamese

    # visualize the results
    def plt_metric(self, history, metric, title, has_valid=True):
        """Plots the given 'metric' from 'history'.

        Arguments:
            history: history attribute of History object returned from Model.fit.
            metric: Metric to plot, a string value present as key in 'history'.
            title: A string to be used as title of plot.
            has_valid: Boolean, true if valid data was passed to Model.fit else false.

        Returns:
            None.
        """
        plt.plot(history[metric])
        if has_valid:
            plt.plot(history["val_" + metric])
            plt.legend(["train", "validation"], loc="upper left")
        plt.title(title)
        plt.ylabel(metric)
        plt.xlabel("epoch")
        plt.show()

        # Plot the accuracy
        self.plt_metric(history=history.history, metric="accuracy", title="Model accuracy")

        # Plot the constrastive loss
        self.plt_metric(history=history.history, metric="loss", title="Constrastive Loss")

        # evaluate the model
        results = self.evaluate([self.x_test_1, self.x_test_2], self.labels_test)
        print("test loss, test acc:", results)

        # visualize the preds
        predictions = self.predict([self.x_test_1, self.x_test_2])
        self.visualize(self.pairs_test, self.labels_test, to_show=3, predictions=predictions, test=True)


    def fit(self):
        # make train pairs
        pairs_train, labels_train = self.make_pairs(self.x_train, self.y_train)

        # make validation pairs
        pairs_val, labels_val = self.make_pairs(self.x_val, self.y_val)

        # make test pairs
        pairs_test, labels_test = self.make_pairs(self.x_test, self.y_test)

        print('pairs_train.shape', pairs_train.shape)

        # split trainig pairs
        x_train_1 = pairs_train[:, 0]  # x_train_1.shape is (60000, 28, 28)
        x_train_2 = pairs_train[:, 1]

        # split validation pairs
        x_val_1 = pairs_val[:, 0]  # x_val_1.shape = (60000, 28, 28)
        x_val_2 = pairs_val[:, 1]

        # split test pairs
        x_test_1 = pairs_test[:, 0]  # x_test_1.shape = (20000, 28, 28)
        x_test_2 = pairs_test[:, 1]

        # inspect training pairs
        self.visualize(pairs_train[:-1], labels_train[:-1], to_show=4, num_col=4)

        # inspect validation pairs
        self.visualize(pairs_val[:-1], labels_val[:-1], to_show=4, num_col=4)

        # inspect test pairs
        self.visualize(pairs_test[:-1], labels_test[:-1], to_show=4, num_col=4)

        # create model
        siamese = self.create_model()
        siamese.compile(loss=self.loss(margin=self.margin), optimizer="RMSprop", metrics=["accuracy"])
        siamese.summary()

        # train the model
        history = siamese.fit(
            [x_train_1, x_train_2],
            labels_train,
            validation_data=([x_val_1, x_val_2], labels_val),
            batch_size=self.batch_size,
            epochs=self.epochs,
        )


if __name__ == '__main__':
    import pandas as pd
    import json

    CONDITION = 'tap'

    def read_json(path):
        collected_data_list = []

        df = pd.read_json(path).T

        for idx, row in df.itertuples():
            mydict = {'pid': idx.split('_')[1], 'data_id': idx, 'usage': idx.split('_')[0]}

            # iterate json and add all columns individually
            for key in row.keys():
                df2 = pd.DataFrame(row[key])
                mydict.update({f'{key}_df': df2.set_index(0)})

            #assert mydict['sensor_acc_df'].shape == \
            #       mydict['sensor_gyro_df'].shape == \
            #       #mydict['sensor_grav_df'].shape == \
            comb_df = pd.concat([mydict['sensor_acc_df'].reset_index(drop=True),
                                 mydict['sensor_grav_df'].reset_index(drop=True),
                                 mydict['sensor_gyro_df'].reset_index(drop=True)], axis=1)
            comb_df.columns = ['acc_x', 'acc_y', 'acc_z',
                               'grav_x', 'grav_y', 'grav_z',
                               'gyro_x', 'gyro_y', 'gyro_z']
            mydict.update({'comb': comb_df})
            collected_data_list.append(mydict)

        return collected_data_list

    def read_devset(path, what):
        js = json.load(open(path))
        ret = []
        for k1 in js.keys():
            for k2 in ['g1', 'g2', 'g3', 'g4']:
                df_sensor_acc =  pd.DataFrame(js[k1][k2][what]['sensor_acc']).set_index(0)
                df_sensor_acc.columns = ['acc_x', 'acc_y', 'acc_z']
                df_sensor_grav = pd.DataFrame(js[k1][k2][what]['sensor_grav']).set_index(0)
                df_sensor_grav.columns = ['grav_x', 'grav_y', 'grav_z']
                df_sensor_gyro = pd.DataFrame(js[k1][k2][what]['sensor_gyro']).set_index(0)
                df_sensor_gyro.columns = ['gyro_x', 'gyro_y', 'gyro_z']
                df_sensor_accl = pd.DataFrame(js[k1][k2][what]['sensor_accl']).set_index(0)
                df_sensor_accl.columns = ['accl_x', 'accl_y', 'accl_z']
                df_sensor_magn = pd.DataFrame(js[k1][k2][what]['sensor_magn']).set_index(0)
                df_sensor_magn.columns = ['magn_x', 'magn_y', 'magn_z']
                df_touch =       pd.DataFrame(js[k1][k2][what]['touch']).set_index(0)
                if what == 'keystroke':
                    df_touch.columns = ['ascii']
                else:
                    df_touch.columns = ['touch_x', 'touch_y', 'touch_action']
                df = pd.concat([df_sensor_acc,
                                df_sensor_grav,
                                df_sensor_gyro,
                                df_sensor_accl,
                                df_sensor_magn,
                                df_touch], axis=1)
                df_interp = df.filter(regex=".*\_[x|y|z]", axis=1)
                df_interp = df_interp.interpolate(method='linear')
                df_ret = df_interp.merge(df, how='left')

                ret.append({'pid': k1, 'session': k2,  'condition': what, 'df': df_ret})
        return ret

    def read_txt(path):
        comparisons = []
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if len(line) > 1:
                    line_split = line.strip().split(' ')
                    comparisons.append({'a': line_split[0], 'b': line_split[1]})
        return comparisons

    tasks = {'keystroke': 1, 'readtext': 2, 'gallery': 3, 'tap': 4}

    comparisons = read_txt(f'C:/Tools/behavdb/Comparisons_ValSet_Task{tasks[CONDITION]}_{CONDITION}_updated.txt')

    data_train = read_json(f'C:/Tools/behavdb/ValSet_Task{tasks[CONDITION]}_{CONDITION}_enrolment.json')
    print("Read enrolment data")
    data_val = read_json(f'C:/Tools/behavdb/ValSet_Task{tasks[CONDITION]}_{CONDITION}_verification.json')
    print("Read verification data")
    devset = read_devset('C:/Tools/behavdb/DevSet.json', CONDITION)
    print('Read DevSet')

    labels = [pid['pid'] for pid in data_train]
    all_labels = set([pid['pid'] for pid in data_train+data_val])

    from sklearn.preprocessing import LabelEncoder
    lb = LabelEncoder().fit(labels)

    error_i = -1
    for dict in data_train + data_val:
        try:
            dict.update({'label': lb.transform([dict['pid']])})
        except ValueError as ve:
            if 'contains previously unseen labels' in str(ve):
                print(f'WARNING {error_i}:', str(ve))
                dict.update({'label': -error_i})
                error_i -= 1



    S = AutoSiameseAuthenticator()
