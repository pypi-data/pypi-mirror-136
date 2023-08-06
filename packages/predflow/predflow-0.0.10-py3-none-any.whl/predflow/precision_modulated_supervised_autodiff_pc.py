'''
Supervised predictive coding with implicit gradients using tensorflow's 
autodifferentiation of the energy with respect to representations and 
learnable parameters, including precision weighting of prediction errors.
'''

import tensorflow as tf
from .pc_utils import *
from .precisions_utils import *

@tf.function
def learn(model, data, target, ir=0.05, lr=0.001, pr=0.001, T=40, predictions_flow_upward=False,
          gamma=tf.constant(0.5)):
    """Implements the following logic::
    
        Initialize representations
        do T times
            E = 0.5 * norm(r - model(r)) ^ 2 + log |P|
            r -= ir * dE/dr
        W -= lr * dE/dW
        P -= pr * dE/dP

    :param model: description of a sequential network by a list of layers,
                  can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.PrecisionModulatedDense`
    :param data: inuput data batch
    :type data: 3d tf.Tensor of float32
    :param target: output target batch
    :type target: 3d tf.Tensor of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param lr: learning rate, defaults to 0.001
    :type lr: float, optional
    :param pr: learning rate for precision, defaults to 0.001
    :type pr: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    """
    
    if predictions_flow_upward:
        representations = forward_initialize_representations(model, data, target)
    else:
        representations = backward_initialize_representations(model, target, data)
    parameters = [param for layer in model for param in layer.trainable_variables]
    weights = [param for param in parameters if param.name[0] == 'w']
    precisions = [param for param in parameters if param.name[0] == 'P']
    
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                energy, autodiff = precision_modulated_energy(model, representations, parameters, 
                                                              predictions_flow_upward=predictions_flow_upward, 
                                                              gamma=gamma)
                inference_SGD_step(representations, ir, autodiff.gradient(energy, representations), 
                                   update_last=False)
    parameters_SGD_step(precisions, pr, autodiff.gradient(energy, precisions))
    parameters_SGD_step(weights, lr, autodiff.gradient(energy, weights))
    
    del autodiff

@tf.function
def infer(model, data, ir=0.05, T=40, predictions_flow_upward=False, target_shape=None):
    """Implements the following logic::
    
        Initialize representations
        do T times
            E = 0.5 * norm(r - model(r)) ^ 2 + log |P|
            r -= ir * dE/dr
        return r

    :param model: description of a sequential network by a list of layers,
                  can be generated e.g. using :py:func:`tf_utils.mlp`
    :type model: list of :py:class:`tf_utils.PrecisionModulatedDense`
    :param data: inuput data batch
    :type data: 3d `tf.Tensor` of float32
    :param ir: inference rate, defaults to 0.05
    :type ir: float, optional
    :param T: number of inference steps, defaults to 40
    :type T: int, optional
    :param predictions_flow_upward: direction of prediction flow, defaults to False
    :type predictions_flow_upward: bool, optional
    :param target_shape: shape of target minibatch, defaults to None
    :type target_shape: 1d tf.Tensor of int32, optional
    :return: latent representations
    :rtype: list of 3d tf.Tensor of float32
    """
    
    if predictions_flow_upward:
        representations = forward_initialize_representations(model, data)
    else:
        representations = zero_initialize_representations(model, data, predictions_flow_upward=predictions_flow_upward, 
                                                          target_shape=target_shape, bias=tf.constant(.0001))
        
    with tf.name_scope("InferenceLoop"):
        for _ in range(T):
            with tf.name_scope("InferenceStep"):
                energy, autodiff = precision_modulated_energy(model, representations,
                                                              predictions_flow_upward=predictions_flow_upward)
                inference_SGD_step(representations, ir, autodiff.gradient(energy, representations))
                
    del autodiff
    
    return representations[1:]