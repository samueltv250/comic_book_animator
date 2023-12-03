import cv2
import numpy as np
from PIL import Image
from PIL import Image, ImageTk
import tkinter as tk
import os

def get_all_file_paths(directory_path):
    """
    Get all file paths in the given directory, including paths in subdirectories.

    Args:
    directory_path (str): The path to the directory from which to get file paths.

    Returns:
    list: A list of paths to the files in the given directory and its subdirectories.
    """
    file_paths = []  # List to store file paths
    for root, directories, files in os.walk(directory_path):
        for filename in files:
            # Join the two strings to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths

def display_image_with_tkinter(image_path):
    # Create a root window
    root = tk.Tk()
    
    # Open the image file
    img = Image.open(image_path)
    
    # Convert the Image object to a TkPhoto object
    tkimage = ImageTk.PhotoImage(img)
    
    # Create a Label widget to display the image
    label = tk.Label(root, image=tkimage)
    label.pack()
    
    # Run the application
    root.mainloop()

def find_contours(image_path):
    # Read the image
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    min_area = (width * height) * 0.05  # Minimum area threshold

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    panels = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue  # Skip contours that are too small

        # Approximate the contour
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.01 * peri, True)

        # Check for a rectangular shape (at least 3 corners)
        if len(approx) >= 3:
            x, y, w, h = cv2.boundingRect(approx)
            new_panel = (x, y, x + w, y + h)

            # Check if the contour is close to a rectangle
            if area / (w * h) > 0.1:
                # Check if this panel overlaps with or is inside any existing panel
                is_unique = True
                for existing_panel in panels:
                    if (new_panel[0] >= existing_panel[0] and new_panel[2] <= existing_panel[2] and
                        new_panel[1] >= existing_panel[1] and new_panel[3] <= existing_panel[3]):
                        # This panel is inside an existing panel, so it's not unique
                        is_unique = False
                        break

                if is_unique:
                    panels.append(new_panel)

    # Sort the panels
    panels.sort(key=lambda x: (x[1], x[0]))

    return panels



def extract_panels(image_path, panels, path_to_save_panels=""):
    with Image.open(image_path) as img:
        extracted_panels = []
        for i, (x, y, w, h) in enumerate(panels):
            panel_image = img.crop((x, y, w, h))
            panel_path = path_to_save_panels + f"panel_{i+1}.png"
            if not os.path.exists(path_to_save_panels):
                os.makedirs(path_to_save_panels)
            panel_image.save(panel_path)
            extracted_panels.append(panel_path)
        return extracted_panels

# Usage


print(get_all_file_paths("invincible"))
image_path = 'invincible/Invincible V1-Zone-012.jpg'
panels = find_contours(image_path)
extracted_panels = extract_panels(image_path, panels, "panels_"+image_path.split('.')[0] + "_panels/")
print(len(extracted_panels))


# Example usage with a list of Image objects
images = [display_image_with_tkinter(image_path) for image_path in extracted_panels]

# for image_path in get_all_file_paths("invincible"):
#     panels = find_contours(image_path)
#     extracted_panels = extract_panels(image_path, panels, image_path.split('.')[0] + "_panels/")
#     print(len(extracted_panels))
#     # # Example usage with a list of Image objects
#     # images = [display_image_with_tkinter(image_path) for image_path in extracted_panels]