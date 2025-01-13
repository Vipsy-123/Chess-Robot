import cv2
import inference
import supervision as sv
import json
import time

annotator = sv.BoxAnnotator()

# # Function to save predictions to a JSON file
def save_predictions(predictions):
    with open('predictions.json', 'w') as json_file:
        json.dump(predictions, json_file)

inference.Stream(
    source = "../media/VID20240128155848.mp4", # To use webcam add 'webcam'
    model = "chessv1-5ew7x/1", # from Universe

    output_channel_order = "BGR",
    use_main_thread = True,

    on_prediction = lambda predictions, image: (
        time.sleep(1),
        print(predictions),
        save_predictions(predictions),
        cv2.imshow(
            "class",
            annotator.annotate(
                scene = image,
                detections = sv.Detections.from_roboflow(predictions)
            )
        ),
        cv2.waitKey(1)
    )
)