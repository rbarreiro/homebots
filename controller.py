import numpy as np

def vector_angle(v1, v2):
    """
    Calculate the signed angle between two vectors in degrees.
    The angle is positive if the rotation from v1 to v2 is counter-clockwise.
    """
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)
    
    if v1_norm == 0 or v2_norm == 0:
        return 0.0  # Avoid division by zero
    
    cos_theta = np.clip(np.dot(v1, v2) / (v1_norm * v2_norm), -1.0, 1.0)
    angle_rad = np.arccos(cos_theta)
    
    # Determine the sign of the angle
    cross_product = np.cross(v1, v2)
    if cross_product < 0:
        angle_rad = -angle_rad
    
    return np.degrees(angle_rad)
    



class RobotState:
    def __init__(self, aruco_points):
        self.aruco_points = aruco_points
        self.center = np.mean(aruco_points, axis=0)
        self.direction = np.mean(aruco_points[[0, 3]], axis=0) - np.mean(aruco_points[[1, 2]], axis=0)
        
    def angle_to_point(self, point):
        """
        Calculate the angle from the robot's center to a point.
        """
        vector_to_point = point - self.center
        return vector_angle(vector_to_point, self.direction)
    
    def distance_to_point(self, point):
        """
        Calculate the Euclidean distance from the robot's center to a point.
        """
        return np.linalg.norm(point - self.center)
    
    def size(self):
        return np.linalg.norm(self.direction)

    def __repr__(self):
        return f"RobotState(aruco_points={self.aruco_points},center={self.center}, direction={self.direction})"
    
    


class Controller:
    def __init__(self, camera, robot, seg, code):
        self.camera = camera
        self.robot = robot
        self.code = code
        self.seg = seg


    def get_state(self):
        ids, corners = self.camera.detect_arucos()
        if ids is not None:
            for i, id in enumerate(ids):
                if id == self.code:               
                    return RobotState(corners[i][0])
        return None
    
    def turn_to_point(self, point, state = None):
        if state is None:
            state = self.get_state()
        d = state.angle_to_point(point)
        while np.abs(d) > 10:
            m = 0.01
            if d > 0:
                self.robot.turn_left(duration=float(d*m))
            else:
                self.robot.turn_right(duration = float(-d*m))
            state = self.get_state()
            d = state.angle_to_point(point)

    def move_straight_to_point(self, point, state=None):
        self.robot.set_arm_angle(30)
        if state is None:
            state = self.get_state()
        if state is None:
            print("ArUco marker not detected.")
            return
        dist = state.distance_to_point(point)
        size = state.size()
        #print(f"dist={dist} size={size}")
        while dist > size:
            #print(f"dist={dist} size={size}")
            self.turn_to_point(point, state)            
            self.robot.forward(duration=float(dist*0.01), speed=0.5)
            state = self.get_state()
            dist = state.distance_to_point(point)
            size = state.size()

    def move_to_point(self, point):
        path = self.seg.get_path(self.camera.get_frame(), tuple(self.get_state().center), point, size=10)
        if len(path) > 0:
            for p in path:
                self.move_straight_to_point(p)
        else:
            print("No path found.")



    def make_path(self, path):
        for p in path:
            self.move_to_point(p)

