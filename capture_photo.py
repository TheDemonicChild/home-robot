import os
import subprocess
import cv2
from utils import logger

def is_raspberry_pi():
    """
    Detects if the program is running on a Raspberry Pi.

    Returns:
        bool: True if running on Raspberry Pi, False otherwise.
    """
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                if "Raspberry Pi" in cpuinfo:
                    print("Raspberry Pi detected")
                    return True
    except Exception as e:
        print("Raspberry Pi NOT detected")
        logger.error(f"Error detecting Raspberry Pi: {e}")
    return False

def capture_photo():
    """
    Captures a photo using libcamera-still on Raspberry Pi or OpenCV on other systems.

    Returns:
        numpy.ndarray or None: Captured image as a NumPy array or None if capture failed.
    """
    if is_raspberry_pi():
        logger.info("Detected Raspberry Pi. Using libcamera-still to capture image.")
        image_path = "/tmp/image.jpg"
        try:
            # Capture image using libcamera-still with a 500ms preview
            subprocess.run(
                ["libcamera-still", "--timeout", "500", "--output", image_path],
                check=True
            )
            # Read the captured image using OpenCV
            img = cv2.imread(image_path)
            if img is None:
                logger.error("libcamera-still captured an empty image.")
                return None
            return img
        except subprocess.CalledProcessError as e:
            logger.error(f"libcamera-still command failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during image capture with libcamera-still: {e}")
            return None
    else:
        logger.info("Non-Raspberry Pi system detected. Using OpenCV to capture image.")
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logger.error("Cannot open camera.")
                return None

            ret, frame = cap.read()
            cap.release()

            if not ret:
                logger.error("Failed to capture image using OpenCV.")
                return None

            return frame
        except Exception as e:
            logger.error(f"Unexpected error during image capture with OpenCV: {e}")
            return None