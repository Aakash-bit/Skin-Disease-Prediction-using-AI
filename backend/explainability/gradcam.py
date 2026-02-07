import tensorflow as tf
import numpy as np
import cv2

def generate_gradcam(model, image, class_index, layer_name=None):
    """
    Generates Grad-CAM heatmap for a given image and class index
    """

    # Automatically find last Conv2D layer if not specified
    if layer_name is None:
        for layer in reversed(model.layers):
            if isinstance(layer, tf.keras.layers.Conv2D):
                layer_name = layer.name
                break

    grad_model = tf.keras.models.Model(
        inputs=model.inputs,
        outputs=[model.get_layer(layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(image)
        loss = predictions[:, class_index]

    # Compute gradients
    grads = tape.gradient(loss, conv_outputs)

    # Global average pooling on gradients
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Convert to NumPy safely
    conv_outputs = conv_outputs[0].numpy()
    pooled_grads = pooled_grads.numpy()

    # Weight the convolution outputs
    heatmap = np.zeros(conv_outputs.shape[:2], dtype=np.float32)

    for i in range(pooled_grads.shape[0]):
        heatmap += pooled_grads[i] * conv_outputs[:, :, i]

    # Apply ReLU
    heatmap = np.maximum(heatmap, 0)

    # Normalize
    if np.max(heatmap) != 0:
        heatmap /= np.max(heatmap)

    return heatmap
