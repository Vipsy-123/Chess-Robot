import cv2
import numpy as np

# Read the image
image = cv2.imread('Chess9.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Use Canny edge detector
edges = cv2.Canny(gray, 50, 150, apertureSize=3)

# Find contours of the chessboard grid
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Calculate intersection points from contours
intersections = []
for cnt in contours:
    for i in range(len(cnt)):
        for j in range(i + 1, len(cnt)):
            pt1 = cnt[i][0]
            pt2 = cnt[j][0]
            if pt1[0] != pt2[0] and pt1[1] != pt2[1]:  # Ensure points are not on the same row or column
                intersections.append((pt1[0], pt2[1]))

# Convert intersection points to numpy array
intersections = np.array(intersections)

# Manually select the bottom two corners
bottom_corners = np.array([
    [np.min(intersections[:, 0]), np.max(intersections[:, 1])],   # Bottom-left corner
    [np.max(intersections[:, 0]), np.max(intersections[:, 1])]   # Bottom-right corner
])

# Estimate the top two corners based on the bottom ones
bottom_left_x, bottom_left_y = bottom_corners[0]
bottom_right_x, bottom_right_y = bottom_corners[1]

# Define a fixed vertical distance between top and bottom corners
vertical_distance = 600

# Calculate the estimated top corners
estimated_top_left_corner = (bottom_left_x + 150, bottom_left_y - vertical_distance)
estimated_top_right_corner = (bottom_right_x - 200, bottom_right_y - vertical_distance)

# Define the source and destination points for perspective transformation
src_pts = np.array([bottom_corners[0], bottom_corners[1], estimated_top_left_corner, estimated_top_right_corner], dtype=np.float32)
dst_pts = np.array([[0, 400], [400, 400],[0, 0], [400, 0], ], dtype=np.float32)

# Calculate the perspective transformation matrix
transform_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)

# Apply the perspective transformation
warped_image = cv2.warpPerspective(image, transform_matrix, (400, 400))

# Resize the warped image to 512x512
resized_image = cv2.resize(warped_image, (512, 512))

# Save the resized image as 'board.jpg'
cv2.imwrite('board.jpg', resized_image)

# Display the resized image
cv2.imshow('Resized Warped Image', resized_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
