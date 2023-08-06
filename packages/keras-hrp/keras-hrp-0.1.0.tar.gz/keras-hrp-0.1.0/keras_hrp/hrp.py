import tensorflow as tf
from typing import List


class HashedRandomProjection(tf.keras.layers.Layer):
    """ The HRP layer

    Parameters:
    -----------
    hyperplane : tf.Tensor (Default: None)
        An existing matrix with weights

    random_state : int (Default: 42)
        Random seed to initialize the hyperplane.

    output_size : int (Default: None)
        The output dimension of the random projection.

    Example:
    --------
    from evidence_model.hrp import HashedRandomProjection
    import tensorflow as tf
    NUM_FEATURES=512
    hrproj = HashedRandomProjection(output_size=1024, random_state=42)
    hrproj.build(input_shape=(NUM_FEATURES,))
    x = tf.random.normal(shape=(2, NUM_FEATURES))
    y = hrproj(x)
    """
    def __init__(self,
                 hyperplane: tf.Tensor = None,
                 random_state: int = 42,
                 output_size: int = None,
                 **kwargs):
        super(HashedRandomProjection, self).__init__(**kwargs)
        self.hyperplane = hyperplane
        self.random_state = random_state
        self.output_size = output_size

    def build(self, input_shape=None):
        # init the not-trainable random hyperplane
        if self.hyperplane is None:
            num_features = input_shape[-1]
            tf.random.set_seed(self.random_state)
            self.hyperplane = tf.Variable(
                initial_value=tf.random.normal(
                    shape=(num_features, self.output_size),
                    mean=0.0, stddev=1.0),
                trainable=False)
        else:
            self.hyperplane = tf.Variable(
                initial_value=self.hyperplane,
                trainable=False, dtype=self.dtype)
        super(HashedRandomProjection, self).build(input_shape)

    def call(self, inputs: tf.Tensor):
        projection = tf.matmul(inputs, self.hyperplane)
        hashvalues = tf.experimental.numpy.heaviside(projection, 0)  # int
        return hashvalues
