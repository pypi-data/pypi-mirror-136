import tensorflow as tf
import pkg_resources
from deepqis.utils import Extract_Net as arlnet
import os

def load():
    """ Return pre-trained model"""
    path_to_model, file_name = os.path.split(__file__)
    stream = pkg_resources.resource_stream(path_to_model, 'models/ARL_ORNL_meas_n_1000_qubits_2_batch_4_alpha_0.4_BEST.h5')
    return stream

def fit(input_data):

    loaded_file = load()
    model = tf.keras.models.load_model(loaded_file, custom_objects={'ErrorNode':arlnet.ErrorNode, \
                                        'PredictDensityMatrix':arlnet.PredictDensityMatrix})

    def scaling_mean_0_std_1(row_matrix):
        m = tf.math.reduce_mean(row_matrix)
        std = tf.math.reduce_std(row_matrix)
        scaled = (row_matrix - m) / std
        return scaled

    x_in = scaling_mean_0_std_1(input_data, [-1, 6, 6, 1])
    logits, dm_pred = model(x_in)

    return dm_pred
# import os
# cwd, f = os.path.split(__file__)
# print(cwd)
# print(f)