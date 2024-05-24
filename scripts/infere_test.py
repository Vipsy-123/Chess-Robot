import cv2
import inference 
import supervision as sv
import json
import time

# Function to save predictions to a JSON file
def save_predictions(predictions):
    with open('predictions.json', 'w') as json_file:
        json.dump(predictions, json_file)

# Initialize the BoxAnnotator
annotator = sv.BoxAnnotator()

# Define the on_prediction callback function
def on_prediction(predictions, image):
    print(predictions)
    # Annotate the image with predictions
    annotated_image = annotator.annotate(
        scene=image,
        detections=sv.Detections.from_roboflow(predictions)
    )
    # Display the annotated image
    cv2.imshow("Chess Image", annotated_image)
    cv2.waitKey(1)
    # Save predictions to JSON file
    save_predictions(predictions)

# Run the inference using inference-gpu
def get_predictions():

    inference.Stream(
        source="chess9.jpg",  # To use webcam add 'webcam'
        model="chessv1-5ew7x/1",  # from Universe

        output_channel_order="BGR",
        use_main_thread=True,

        on_prediction=on_prediction
    )
    return predictions

# Main loop to periodically save predictions
while True:
    time.sleep(3)  # Sleep for 2-3 seconds
    # Get predictions from inference-gpu (if needed)
    predictions = get_predictions()
    # Save predictions to JSON file
    save_predictions(predictions)
