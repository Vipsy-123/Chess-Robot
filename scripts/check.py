<<<<<<< HEAD
'''
Code Description:

1] This script loads predictions and chessboard centers from JSON files, then matches each prediction to the closest square on the chessboard.
2] It prints the prediction IDs along with the corresponding square positions on the chessboard if a valid square is found within the threshold.
3] If no valid square is found within the threshold, it indicates that in the output.
'''

import json

# Load JSON data from files
with open('../saved_files/chessboard_centers.json') as json_file:
    board_centers = json.load(json_file)

with open('../saved_files/predictions.json') as json_file2:
    predictions = json.load(json_file2)

# Define threshold
thresh = 35

# Mapping classes to piece name
class_mapping = {
    "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
    "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
}

# Print the class mapping
print("Class Mapping:")
for class_id, piece_name in class_mapping.items():
    print(f"Class ID: {class_id} -> Piece Name: {piece_name}")

print("\nPredictions:")

# Process each prediction
for selected_prediction in predictions:
    # Get the prediction ID and class name
    prediction_id = selected_prediction["detection_id"]
    class_name = selected_prediction["class_name"]

    # Obtain a prediction coordinate from json file
    pred_x = selected_prediction["bounding_box"]["x"]
    pred_y = selected_prediction["bounding_box"]["y"]

    closest_square = None
    in_box = False
    for square, coord in board_centers.items():
        square_x, square_y = coord
        # distance = np.sqrt((pred_x - square_x)**2 + (pred_y - square_y)**2)
        if(abs(square_x - pred_x) <= thresh and abs(square_y - pred_y) <=thresh):
            in_box = True
            closest_square = square
            break

    # Ensure a closest square is found within the threshold
    if closest_square and in_box:
        print(f"Prediction with ID {prediction_id} placed at square {closest_square} ({class_mapping[class_name]})")
    else:
        print(f"NOT VALID Id :{prediction_id} ({class_mapping[class_name]})")
=======
'''
Code Description:

1] This script loads predictions and chessboard centers from JSON files, then matches each prediction to the closest square on the chessboard.
2] It prints the prediction IDs along with the corresponding square positions on the chessboard if a valid square is found within the threshold.
3] If no valid square is found within the threshold, it indicates that in the output.
'''

import json

# Load JSON data from files
with open('../saved_files/chessboard_centers.json') as json_file:
    board_centers = json.load(json_file)

with open('../saved_files/predictions.json') as json_file2:
    predictions = json.load(json_file2)

# Define threshold
thresh = 35

# Mapping classes to piece name
class_mapping = {
    "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
    "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
}

# Print the class mapping
print("Class Mapping:")
for class_id, piece_name in class_mapping.items():
    print(f"Class ID: {class_id} -> Piece Name: {piece_name}")

print("\nPredictions:")

# Process each prediction
for selected_prediction in predictions:
    # Get the prediction ID and class name
    prediction_id = selected_prediction["detection_id"]
    class_name = selected_prediction["class_name"]

    # Obtain a prediction coordinate from json file
    pred_x = selected_prediction["bounding_box"]["x"]
    pred_y = selected_prediction["bounding_box"]["y"]

    closest_square = None
    in_box = False
    for square, coord in board_centers.items():
        square_x, square_y = coord
        # distance = np.sqrt((pred_x - square_x)**2 + (pred_y - square_y)**2)
        if(abs(square_x - pred_x) <= thresh and abs(square_y - pred_y) <=thresh):
            in_box = True
            closest_square = square
            break

    # Ensure a closest square is found within the threshold
    if closest_square and in_box:
        print(f"Prediction with ID {prediction_id} placed at square {closest_square} ({class_mapping[class_name]})")
    else:
        print(f"NOT VALID Id :{prediction_id} ({class_mapping[class_name]})")
>>>>>>> 496c3f9811ac762dd63ac4d13a2b773204ca4f2d
