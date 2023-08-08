import io
import numpy as np
from keras.applications import ResNet50  # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions  # type: ignore
from tensorflow.keras.preprocessing import image  # type: ignore

# Load the pre-trained ResNet-50 model
model = ResNet50(weights="imagenet")
from PIL import Image, ImageChops


def error_level_analysis(image: bytes, quality: int = 90, threshold: int = 10) -> bool:
    original = Image.open(io.BytesIO(image))
    temp_file = io.BytesIO()
    original.save(temp_file, format="JPEG", quality=quality)
    recompressed = Image.open(temp_file)
    diff = ImageChops.difference(original, recompressed)
    diff = diff.convert("L")
    mean_diff: int = diff.getextrema()[1]  # type: ignore
    return mean_diff < threshold  # type: ignore


def is_morphed(image_path: str) -> bool:
    img = image.load_img(image_path, target_size=(224, 224))  # type: ignore
    img_array = image.img_to_array(img)  # type: ignore
    img_array = np.expand_dims(img_array, axis=0)  # type: ignore
    img_array = preprocess_input(img_array)  # type: ignore

    predictions = model.predict(img_array)  # type: ignore
    decoded_predictions = decode_predictions(predictions, top=1)[0]  # type: ignore

    # You can modify this threshold based on your model's performance
    confidence_threshold: float = 0.75
    confidence: float = decoded_predictions[0][2]  # type: ignore
    return confidence < confidence_threshold  # type: ignore
