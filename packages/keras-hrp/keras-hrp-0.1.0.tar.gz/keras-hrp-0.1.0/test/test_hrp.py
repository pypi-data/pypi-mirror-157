import keras_hrp as khrp
import tensorflow as tf
import numpy as np


def test_1():
    """ The initialized hyperplane should have always the same weights
          for the given default PRNG seed.
    """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = tf.random.normal(shape=(BATCH_SIZE, NUM_FEATURES))
    # instantiate layer without telling the seed
    layer = khrp.HashedRandomProjection(output_size=OUTPUT_SIZE)
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    # instantiate another layer
    layer2 = khrp.HashedRandomProjection(output_size=OUTPUT_SIZE)
    outputs2 = layer2(inputs)
    assert outputs2.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert tf.math.reduce_all(outputs == outputs2)


def test_2():
    """ Different PRNG seeds should lead to different hyperplanes """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = tf.random.normal(shape=(BATCH_SIZE, NUM_FEATURES))
    # instantiate layer without telling the seed
    layer = khrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, random_state=23)
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    # instantiate another layer
    layer2 = khrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, random_state=42)
    outputs2 = layer2(inputs)
    assert outputs2.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert not tf.math.reduce_all(outputs == outputs2)
    assert not tf.math.reduce_all(layer.hyperplane == layer2.hyperplane)


def test_3():
    """ The hyperplane can be set as input argument """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = tf.random.normal(shape=(BATCH_SIZE, NUM_FEATURES))
    # create hyperplane as numpy array
    myhyperplane = np.random.randn(NUM_FEATURES, OUTPUT_SIZE)
    layer = khrp.HashedRandomProjection(hyperplane=myhyperplane)
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert tf.math.reduce_all(layer.hyperplane == myhyperplane)
