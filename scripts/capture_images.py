import cv2
import os
import datetime

# Create a directory to save images if it doesn't exist
save_dir = 'captured_images'
os.makedirs(save_dir, exist_ok=True)

# Initialize the webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Image capture loop
image_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    cv2.imshow('Camera', frame)

    # Wait for key press
    key = cv2.waitKey(1) & 0xFF

    # Save the image when 's' is pressed
    if key == ord('s'):
        # Create a unique filename using the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
        filepath = os.path.join(save_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"Image saved as {filepath}")

        # Increment the counter
        image_count += 1

    # Exit when 'q' is pressed
    elif key == ord('q'):
        break

# Release the webcam and close windows
cap.release()
cv2.destroyAllWindows()
