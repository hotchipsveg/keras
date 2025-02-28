"""E2E Tests for mnist_model."""

from keras import backend
from keras.dtensor import integration_test_utils
from keras.dtensor import optimizers as optimizer_lib
from keras.utils import tf_utils

import tensorflow.compat.v2 as tf

from keras.dtensor.python import mesh_util
from keras.dtensor.python import tpu_util
from keras.dtensor.tests import test_util
from tensorflow.dtensor import python as dtensor  # pylint: disable=g-direct-tensorflow-import


class MnistTest(test_util.DTensorBaseTest):

  def test_mnist_training_cpu(self):
    devices = tf.config.list_physical_devices('CPU')
    tf.config.set_logical_device_configuration(
        devices[0], [tf.config.LogicalDeviceConfiguration(),] * 8)

    mesh = mesh_util.create_mesh(
        devices=['CPU:%d' % i for i in range(8)], mesh_dims=[('batch', 8)])

    backend.enable_tf_random_generator()
    # Needed by keras initializers.
    tf_utils.set_random_seed(1337)

    model = integration_test_utils.get_model_with_layout_map(
        integration_test_utils.get_all_replicated_layout_map(mesh))

    optimizer = optimizer_lib.Adam(learning_rate=0.001, mesh=mesh)
    optimizer.build(model.trainable_variables)

    train_losses = integration_test_utils.train_mnist_model_batch_sharded(
        model, optimizer, mesh, num_epochs=3, steps_per_epoch=100,
        global_batch_size=64)
    # Make sure the losses are decreasing
    self.assertEqual(train_losses, sorted(train_losses, reverse=True))

  def DISABLED_test_mnist_training_tpu(self):
    # TODO(scottzhu): Enable TPU test once the dtensor_test rule is migrated out
    # of learning/brain
    tpu_util.dtensor_initialize_tpu_system()
    total_tpu_device_count = dtensor.num_global_devices('TPU')
    mesh_shape = [total_tpu_device_count]
    mesh = tpu_util.create_tpu_mesh(['batch'], mesh_shape, 'tpu_mesh')

    # Needed by keras initializers.
    tf_utils.set_random_seed(1337)

    model = integration_test_utils.get_model_with_layout_map(
        integration_test_utils.get_all_replicated_layout_map(mesh))

    optimizer = optimizer_lib.Adam(learning_rate=0.001, mesh=mesh)
    optimizer.build(model.trainable_variables)

    train_losses = integration_test_utils.train_mnist_model_batch_sharded(
        model, optimizer, mesh, num_epochs=3, steps_per_epoch=100,
        global_batch_size=64)
    # Make sure the losses are decreasing
    self.assertEqual(train_losses, sorted(train_losses, reverse=True))


if __name__ == '__main__':
  tf.test.main()
