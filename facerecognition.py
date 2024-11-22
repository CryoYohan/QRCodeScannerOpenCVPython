import cv2
import sys

# Check if the cascade file path is provided, otherwise use a default path
if len(sys.argv) > 1:
    cascPath = sys.argv[1]
else:
    cascPath = "haarcascade_frontalface_default.xml"  # Update this path if necessary

# Load the Haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# Check if the Haar cascade is loaded successfully
if faceCascade.empty():
    print(f"Error: Could not load Haar cascade from {cascPath}")
    sys.exit(1)

# Initialize the video capture
video_capture = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    if not ret:
        print("Error: Could not read frame from the camera.")
        break

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw rectangles around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
video_capture.release()
cv2.destroyAllWindows()
