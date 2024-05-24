
'''  
    Code Description:-

    1] This script sets up an inference pipeline to detect corners of a chessboard in a live video stream from a webcam.
    2] It annotates the detected corners on the video frame and extracts the chessboard image.
    3] The extracted Chessboard image is then saved for further processing.


'''
import cv2
from inference import InferencePipeline
from inference.models.utils import get_roboflow_model
from inference.core.interfaces.camera.entities import VideoFrame
import supervision as sv
import numpy as np
import time
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")
# Create a simple box annotator to use in our custom sink
annotator = sv.BoxAnnotator()

# Load the model
model = get_roboflow_model(model_id="chess-corner-detection/1", api_key="oJrlpFzFT49RMEIXZJoN")

# Track the time of the last frame processing
last_frame_time = time.time()

# Function to calculate the center point of a bounding box
def calculate_center(box):
    x1, y1, x2, y2 = box
    return [(x1 + x2) // 2, (y1 + y2) // 2]

def order_points(pts):
    # order a list of 4 coordinates:
    # 0: top-left,
    # 1: top-right
    # 2: bottom-right,
    # 3: bottom-left
    
    rect = np.zeros((4, 2), dtype = "float32")
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

# Function to extract chessboard image using TL, TR, BL, BR corners
def extract_chessboard(image, corners):
    # Calculate the center point of each corner
    center_tl = calculate_center(corners[0])
    center_tr = calculate_center(corners[1])
    center_br = calculate_center(corners[2])
    center_bl = calculate_center(corners[3])

    centers = [center_tl,center_tr,center_br,center_bl]
    # Sort corners_centers in the order: top-left, top-right, bottom-right, bottom-left
    corner = np.array(centers)
    ordered_corners = np.array([corner[np.argmin(np.sum(corner, axis=1))],
                                corner[np.argmin(np.diff(corner, axis=1))],
                                corner[np.argmax(np.sum(corner, axis=1))],
                                corner[np.argmax(np.diff(corner, axis=1))]], dtype=np.float32)
    # Define the dimensions of the output chessboard image
    width = max(np.linalg.norm(ordered_corners[0] - ordered_corners[1]),
                np.linalg.norm(ordered_corners[2] - ordered_corners[3]))
    height = max(np.linalg.norm(ordered_corners[1] - ordered_corners[2]),
                 np.linalg.norm(ordered_corners[3] - ordered_corners[0]))

    # Create a destination array to hold the transformed image
    dst_points = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(ordered_corners, dst_points)

    # Warp the image
    warped_image = cv2.warpPerspective(image, M, (int(width), int(height)))

    return warped_image

def my_custom_sink(predictions: dict, video_frame: VideoFrame):
    global last_frame_time
    
    # Get the text labels for each prediction
    labels = [p["class"] for p in predictions.get("predictions", [])]
    # Load predictions into the Supervision Detections API
    detections = sv.Detections.from_inference(predictions)
    print("Coordinates: ", detections.xyxy)
    
    # Calculate time taken for processing the last frame
    current_time = time.time()
    processing_time = current_time - last_frame_time
    last_frame_time = current_time
       
    # Annotate the frame using Supervision annotator, the video_frame, the predictions, and the labels
    annotated_image = annotator.annotate(
        scene=video_frame.image.copy(), detections=detections, labels=labels
    )
    # Display the annotated image
    cv2.imshow("Predictions", annotated_image)
    cv2.waitKey(10)
    
    if "predictions" in predictions and len(predictions["predictions"]) == 4:
        # Extract chessboard image using TL, TR, BL, BR corners
        chessboard_image = extract_chessboard(video_frame.image, detections.xyxy)
        cv2.imwrite("../saved_files/board.png", chessboard_image)
        # Add a delay after saving the image (for example, 1 second)
        time.sleep(.001) 

pipeline = InferencePipeline.init(
    model_id="chess-corner-detection/1",
    api_key="oJrlpFzFT49RMEIXZJoN", # chess-corner-detection/1
    video_reference=0, # To Use Mobile camera stream as webcam - 1, For video use - "../media/document_6064252294466113797.mp4"
    on_prediction=my_custom_sink
)


pipeline.start()
pipeline.join()

