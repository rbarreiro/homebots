import matplotlib.pyplot as plt
import cv2
from PIL import Image

def show_bin_img(x):
    fig, ax = plt.subplots(figsize=(8, 6))  # Ajuste o tamanho conforme necessário
    im = ax.imshow(x, cmap='gray')  # Inicializar com um frame
    plt.show()

def show_img(x):
    fig, ax = plt.subplots(figsize=(8, 6))  # Ajuste o tamanho conforme necessário
    im = ax.imshow(cv2.cvtColor(x, cv2.COLOR_BGR2RGB))  # Inicializar com um frame
    plt.show()

def opencv_to_pil(opencv_image):
    """
    Convert an OpenCV image (BGR format) to a PIL Image (RGB format).
    """
    return Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))