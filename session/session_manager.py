import base64
import io

import numpy as np
from PIL import Image

import face_recognition


def remove_base64_header(image_base64):
    return image_base64.split("base64,")[1]


def read_image_from_request(json_data):
    image_base64 = json_data['image']
    image_base64_no_header = remove_base64_header(image_base64)
    image_data = base64.b64decode(image_base64_no_header)
    im = Image.open(io.BytesIO(image_data))
    im = im.convert('RGB')
    return np.array(im)


def handle_recognition_request(json_data):
    image = read_image_from_request(json_data)
    n_faces = len(face_recognition.face_locations(image))
    return n_faces
