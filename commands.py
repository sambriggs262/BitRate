"""Command execution functions for BitRate voice assistant.

Handles local system tasks like screenshots, app launches, and web navigation.

Author: Sam Briggs
"""

import os
import webbrowser
import subprocess
import datetime
import cv2
import numpy as np
from PIL import ImageGrab


def capture_screen():
    """Capture and save a screenshot to disk using PIL and OpenCV.

    Returns:
        str: Status message with file path or error info.
    """
    try:
        screen = ImageGrab.grab(bbox=None)
        screen_np = np.array(screen)
        screen_cv = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        file_path = f'C:/screencapture/screencapture_{
            datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        cv2.imwrite(file_path, screen_cv)
        return f"Screenshot saved as {file_path}"
    except Exception as e:
        return f"Error capturing screen: {e}"


def open_app(app_path):
    """Open a local application using subprocess.

    Args:
        app_path (str): File path to the application.

    Returns:
        str: Status message indicating success or error.
    """
    try:
        subprocess.Popen(app_path)
        return f"Opened application: {app_path}"
    except Exception as e:
        return f"An error occurred while trying to open {app_path}:{e}"


def handle_web_command(command):
    """Handle voice commands related to web browsing.

    Args:
        command (str): The spoken command string.

    Returns:
        str | None: Status message or None if no match.
    """
    if "browser" in command:
        webbrowser.open("https://www.google.com")
        return "Opened Google"
    elif "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opened YouTube"
    return None


def shutdown():
    """Initiate a system shutdown.

    Returns:
        str: Confirmation message.
    """
    os.system("shutdown /s /t 1")
    return "Shutdown command issued"
