import cv2
import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
from PIL import Image

class ToyDetector:
    def __init__(self):
        model_id = "IDEA-Research/grounding-dino-base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(self.device)
        self.prompt = "a toy. a shoe."

    def detect_opencv(self, opencv_image, text = None):
        image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
        return self.detect(image, text)

    def detect(self, image, text = None):
        if text is None:
            text = self.prompt
        
        inputs = self.processor(images=image, text=text, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        return self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            box_threshold=0.4,
            text_threshold=0.3,
            target_sizes=[image.size[::-1]]
        )


