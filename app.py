from flask import Flask, request, jsonify, render_template
import numpy as np
import base64
from PIL import Image
import io
import tensorflow as tf
import matplotlib.pyplot as plt


# Loading model
model = tf.keras.models.load_model('mnist_model.keras')

app = Flask(__name__)

# Debug function to plot an image
def plot_image(image, title):
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.show()

def preprocess_image(image):
    # 1. Decode base64 image
    image_data = base64.b64decode(image.split(',')[1])
    # 2. Open base64 image
    image = Image.open(io.BytesIO(image_data))
    # 3. Resize image
    image = image.resize((28, 28))
    # 4. Get grayscale (remove Red, Green, Blue)
    r,g,b,a = image.split()
    # 5. Get the array of the grayscale
    img_array = np.array(a)
    # 6. Normalize the values (0~255 -> 0~1)
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=-1)  # Add the channel dimension
    img_array = np.expand_dims(img_array, axis=0)   # Add the batch dimension
    return img_array


def highest_probs(array):
    array = array * 100
    array_dict = {i: array[0, i] for i in range(array.shape[1])}

    # Sort the dict
    sorted_items = sorted(array_dict.items(), key=lambda x: x[1], reverse=True)
    first_max_index, first_max_value = sorted_items[0] # Highest value
    second_max_index, second_max_value = sorted_items[1] # Second Highest

    return jsonify({ 
        'first_index': int(first_max_index),
        'first_prob' : float(first_max_value),
        'second_index': int(second_max_index),
        'second_prob' : float(second_max_value),
        })


### Routes ###
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # 1. Get image from request json
    image_data = request.get_json()
    # 2. Preprocess image
    image_array = preprocess_image(image_data['image'])
    # 3. Predict which number it is 
    prediction = model.predict(image_array)
    #highest_probs(prediction)
    # 4. Select the number that has the highest probablility
    #predicted_number = np.argmax(prediction)
    return highest_probs(prediction)



if __name__ == '__main__':
    app.run(debug=True)