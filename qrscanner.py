import cv2

# Initialize the camera
cap = cv2.VideoCapture(0)

# Initialize the QRCode detector
detector = cv2.QRCodeDetector()

while True:
    _, img = cap.read()

    # Detect and decode
    data, bbox, _ = detector.detectAndDecode(img)

    # Check if there is a QRCode in the image
    if bbox is not None:
        # Display the image with lines
        for i in range(len(bbox)):
            # Convert float coordinates to integers
            point1 = tuple(map(int, bbox[i][0]))
            point2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
            # Draw all lines
            cv2.line(img, point1, point2, color=(255, 0, 0), thickness=2)

        if data:
            print("[+] QR Code detected, data:", data)

    # Display the result
    cv2.imshow("img", img)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
