from transformers import MaskFormerImageProcessor, MaskFormerForInstanceSegmentation
from PIL import Image
import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.ndimage import binary_dilation
import matplotlib.cm as cm

def distance(p1, p2):
    """
    Calculate the Euclidean distance between two points.
    """
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def reconstruct_path(came_from, current):
    """
    Reconstruct the path from the start to the goal.
    """
    total_path = [current]
    while current in came_from:
        current = came_from[current]
        total_path.append(current)
    return total_path[::-1]  # Return reversed path

def get_neighbors(node, grid):
    """
    Get the valid neighbors of a node in the grid.
    """
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        neighbor = (node[0] + dx, node[1] + dy)
        if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
            if grid[neighbor]:  # Assuming 0 is walkable
                neighbors.append(neighbor)
    return neighbors

def aStar(start, goal, grid):
    """
    A* algorithm to find the shortest path from start to goal in a grid.
    """
    open_set = {start}
    came_from = {}
    
    g_score = {start: 0}
    f_score = {start: distance(start, goal)}

    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float('inf')))

        if current == goal:
            return reconstruct_path(came_from, current)

        open_set.remove(current)
        
        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + distance(neighbor, goal)
                open_set.add(neighbor)

    return []

class ImageSeg:

    def __init__(self):
        checkpoint_name = "facebook/maskformer-swin-small-coco"
        self.processor = MaskFormerImageProcessor.from_pretrained(checkpoint_name)
        self.model = MaskFormerForInstanceSegmentation.from_pretrained(checkpoint_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()
        
        self.nav_ids = []
        for k,v in self.model.config.id2label.items():
            if v.startswith("ground") or v.startswith("rug") or v.startswith("floor") or v.startswith("road"):
                self.nav_ids.append(k)
        


    def get_segmentation(self, opencv_image):
        # Convert OpenCV image (BGR) to PIL image (RGB)
        image = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))

        inputs = self.processor(image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)

        return self.processor.post_process_semantic_segmentation(outputs, target_sizes=[image.size[::-1]])[0].cpu()


    def draw_semantic_segmentation(self, segmentation):
        # get the used color map
        viridis = cm.get_cmap('viridis', torch.max(segmentation))
        # get all the unique numbers
        labels_ids = torch.unique(segmentation).tolist()
        fig, ax = plt.subplots()
        ax.imshow(segmentation)
        handles = []
        for label_id in labels_ids:
            label = self.model.config.id2label[label_id]
            color = viridis(label_id)
            handles.append(mpatches.Patch(color=color, label=label))
        ax.legend(handles=handles)
        #return fig
    
    def get_nav_map(self, opencv_image, size=1):
        seg = self.get_segmentation(opencv_image)
        seg = np.array(seg)
        seg = np.where(np.isin(seg, self.nav_ids), False, True)
        seg = binary_dilation(seg, iterations=size)
        return np.invert(seg)
    
    def get_path(self, opencv_image, start, goal, size=1):
        seg = self.get_nav_map(opencv_image, size)
        path = aStar(start, goal, seg)
        return path