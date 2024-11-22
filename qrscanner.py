import cv2

# Initialize the camera
cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

# Set the resolution for better image quality (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, img = cap.read()
    if not ret:
        print("Error: Unable to access the camera.")
        break

    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Preprocess the image for better QR code detection
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)

    # Detect and decode the QR code
    data, bbox, _ = detector.detectAndDecode(binary)

    if bbox is not None and len(bbox) > 0:
        # If a QR code is detected, draw the bounding box and print the data
        for i in range(len(bbox)):
            point1 = tuple(map(int, bbox[i][0]))
            point2 = tuple(map(int, bbox[(i + 1) % len(bbox)][0]))
            cv2.line(img, point1, point2, color=(0, 255, 0), thickness=2)

        if data:
            cv2.putText(img, f"QR Code: {data}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2, cv2.LINE_AA)
            print("[+] QR Code Data:", data)
        else:
            cv2.putText(img, "QR Code detected but no data decoded!", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
    else:
        # No QR code detected, display message in red
        cv2.putText(img, "No QR Code detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 255), 2, cv2.LINE_AA)
        print("[-] No QR Code detected.")

    # Display the image
    cv2.imshow("QR Code Scanner", img)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
