import os
import sys
import pyautogui
import pygetwindow as gw
import time
import threading
from pystray import Icon, MenuItem, Menu
from PIL import Image
from pynput import keyboard

# Global variable to track if a key is pressed
key_pressed = False

# Function to press Ctrl+S
def save_solidworks():
    pyautogui.hotkey('ctrl', 's')

# Check if SolidWorks window is active
def is_solidworks_active():
    windows = gw.getWindowsWithTitle('SOLIDWORKS')
    if windows:
        return windows[0].isActive
    return False

# Keyboard listener: set flag when a key is pressed or released
def on_press(key):
    global key_pressed
    key_pressed = True

def on_release(key):
    global key_pressed
    key_pressed = False

# Start the keyboard listener in a separate thread
def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Run the save function every 5 minutes (300 seconds) if SolidWorks has focus and no key is pressed
def start_auto_save(interval=300):
    while running:  # Only run while the script is running
        if is_solidworks_active() and not key_pressed:  # Check if no key is being pressed
            save_solidworks()
        time.sleep(interval)

# Create an icon from the provided logo
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def create_image():
    # Load the SolidWorks logo (replace with the path to your image)
    image_path = resource_path("swsave.png")
    image = Image.open(image_path)
    return image

# Start/stop the script using the tray icon
def setup_tray_icon():
    def on_quit(icon, item):
        global running
        running = False
        icon.stop()

    menu = Menu(MenuItem('Quit', on_quit))
    icon = Icon("SolidWorks AutoSave", create_image(), menu=menu)
    icon.title = "SolidWorks AutoSave is running"
    icon.run()

# Main function to run autosave in the background
def main():
    global running
    running = True

    # Start the keyboard listener in a separate thread
    listener_thread = threading.Thread(target=start_keyboard_listener)
    listener_thread.daemon = True
    listener_thread.start()

    # Start the autosave script in a separate thread
    autosave_thread = threading.Thread(target=start_auto_save, args=(150,))  # Autosave every 5 minutes
    autosave_thread.daemon = True
    autosave_thread.start()

    # Setup the system tray icon
    setup_tray_icon()

if __name__ == "__main__":
    main()