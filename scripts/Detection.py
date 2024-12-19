import cv2
from inference.models.utils import get_roboflow_model
from inference.core.nms import w_np_non_max_suppression
import supervision as sv
import json
import time

# Load the model
model = get_roboflow_model(model_id="che-jqbyk/6", api_key="5wYIwfVPqdeD3B9yZMfU")

# Define NMS parameters
conf_thresh = 0.20  # Confidence threshold
iou_thresh = 0.50   # IOU threshold
max_detections = 32 # Maximum number of detections

# Define a loop for continuous inference
while True:
    try:
        # Read the image
        image = cv2.imread("../saved_files/board.png")
        # Resizing is very important dont comment this
        image = cv2.resize(image, (680, 680))

        # Perform inference on the image
        results = model.infer(image)[0]
        # print (results)
        detections = sv.Detections.from_inference(results)
        # detections_nms = sv.Detections.with_nms(detections,threshold=0.75, class_agnostic=True)

        annotated_image = sv.BoundingBoxAnnotator().annotate(scene=image, detections=detections)

        # Convert detections to JSON format
        predictions_data = []
        object_count = 0
        existing_predictions = []
        for prediction in results.predictions:
            if prediction.confidence > conf_thresh :
                if(prediction.class_name == "1" or prediction.class_name == "7" or  prediction.class_name == "3" or prediction.class_name == "9"):
                    prediction_dict = {
                        "detection_id": prediction.detection_id,
                        "class_name": prediction.class_name,
                        "class_id": prediction.class_id,
                        "bounding_box": {
                            "x": prediction.x,
                            "y": prediction.y + 25,
                            "width": prediction.width,
                            "height": prediction.height
                        },
                        "confidence": prediction.confidence
                    }
                elif (prediction.class_name == "6" or prediction.class_name == "3" or prediction.class_name == "6" or prediction.class_name == "12"):
                    prediction_dict = {
                        "detection_id": prediction.detection_id,
                        "class_name": prediction.class_name,
                        "class_id": prediction.class_id,
                        "bounding_box": {
                            "x": prediction.x,
                            "y": prediction.y + 30,
                            "width": prediction.width,
                            "height": prediction.height
                        },
                        "confidence": prediction.confidence
                    }
                elif(prediction.class_name == "2" or prediction.class_name == "5" or prediction.class_name == "8" or prediction.class_name == "11"  or prediction.class_name == "10" or prediction.class_name == "4"):
                    prediction_dict = {
                        "detection_id": prediction.detection_id,
                        "class_name": prediction.class_name,
                        "class_id": prediction.class_id,
                        "bounding_box": {
                            "x": prediction.x,
                            "y": prediction.y + 12,
                            "width": prediction.width,
                            "height": prediction.height
                        },
                        "confidence": prediction.confidence
                    }
                else:
                    prediction_dict = {
                        "detection_id": prediction.detection_id,
                        "class_name": prediction.class_name,
                        "class_id": prediction.class_id,
                        "bounding_box": {
                            "x": prediction.x,
                            "y": prediction.y,
                            "width": prediction.width,
                            "height": prediction.height
                        },
                        "confidence": prediction.confidence
                    }
            # # Check if a similar prediction already exists within a threshold around x and y coordinates
            # should_add_prediction = True
            # for existing_prediction in existing_predictions:
            #     if abs(existing_prediction["bounding_box"]["x"] - prediction.x) < 20 and \
            #        abs(existing_prediction["bounding_box"]["y"] - prediction.y) < 20:
            #         should_add_prediction = False
            #         break
            # if should_add_prediction:
            
            #     existing_predictions.append(prediction_dict)
            
            predictions_data.append(prediction_dict)
            object_count += 1

        # Write the predictions data to a JSON file
        with open("../saved_files/predictions.json", "w") as json_file:
            json.dump(predictions_data, json_file, indent=4)

        # Print the total number of objects detected
        print("Total Objects Detected:", object_count)

        # Display the annotated image
        cv2.imshow("Annotated Image", annotated_image)
        # Wait for 1 second (1000 milliseconds)
        cv2.waitKey(2000)

    except Exception as e:
        print("Error:", e)
        # print("Image not available. Retrying in a second...")
        time.sleep(1)
        continue