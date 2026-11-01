#This script allows to  convert model weight from keras to onnx
# pip install tf2onnx
import tf2onnx
from tensorflow import keras
import tensorflow as tf

model=keras.models.load_model(r'C:\Users\talel\OneDrive\Documents\GitHub\Computer_vision\Computer_vision\task2_number_detection\model_mnist_0.keras')
spec = (tf.TensorSpec((None, 28, 28, 1), tf.float32, name="input"),)
model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec, opset=13, output_path="digit_model.onnx")
