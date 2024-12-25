import cv2
import time

def capture_photo():
    """
    Captures a single photo from the default camera and returns the image data.

    Returns:
        frame (numpy.ndarray): The captured image frame.
        None: If the camera cannot be opened or the frame cannot be read.
    """
    # Initialize the camera (0 is usually the built-in camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return None

    # Allow the camera to warm up
    time.sleep(2)

    # Read a single frame
    ret, frame = cap.read()

    if not ret:
        print("Error: Can't receive frame (stream end?). Exiting ...")
        cap.release()
        return None

    # Release the camera
    cap.release()

    # Return the raw image data
    return frame