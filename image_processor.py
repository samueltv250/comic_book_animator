import cv2
import numpy as np
from PIL import Image
from PIL import Image, ImageTk
import tkinter as tk
import os

import pytesseract


def expand_to_boundary(space, panels, image_shape):
    left, top, right, bottom = space
    max_x, max_y = image_shape[1], image_shape[0]

    # Check if the current space intersects any panel
    def intersects_panel(x1, y1, x2, y2):
        for panel in panels:
            if not (x2 <= panel[0] or x1 >= panel[2] or y2 <= panel[1] or y1 >= panel[3]):
                return True
        return False

    # Expand to the left
    while left > 0 and not intersects_panel(left - 1, top, right, bottom):
        left -= 1

    # Expand to the right
    while right < max_x and not intersects_panel(left, top, right + 1, bottom):
        right += 1

    # Expand upwards
    while top > 0 and not intersects_panel(left, top - 1, right, bottom):
        top -= 1

    # Expand downwards
    while bottom < max_y and not intersects_panel(left, top, right, bottom + 1):
        bottom += 1

    return [left, top, right, bottom]





def find_empty_spaces(image, panels, min_area=0.01):
    

    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Mask out the panels by making them black
    for x1, y1, x2, y2 in panels:
        gray[y1:y2, x1:x2] = 255
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    empty_spaces = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area * image.shape[0] * image.shape[1]:
            continue  # Skip small areas

        x, y, w, h = cv2.boundingRect(contour)
        empty_space = [x, y, x + w, y + h]
        

        # Check if the empty space is not a panel
        if not any(is_overlap(empty_space, panel) for panel in panels):
            empty_spaces.append(empty_space)

    # Merge close empty spaces
    merge_threshold = 0.05 * min(image.shape[0], image.shape[1])  # 5% of the smaller dimension
    empty_spaces = merge_close_spaces(empty_spaces, merge_threshold)
    empty_spaces_out = []
    for space in empty_spaces:
        empty_spaces_out.append(expand_to_boundary(space, panels, image.shape))
    

    return empty_spaces_out

def is_overlap(space1, space2):
    return not (space1[2] <= space2[0] or space1[0] >= space2[2] or
                space1[3] <= space2[1] or space1[1] >= space2[3])

def merge_close_spaces(spaces, threshold):
    merged = []
    while spaces:
        current = spaces.pop(0)
        for i, other in enumerate(spaces):
            if is_close(current, other, threshold):
                current = [min(current[0], other[0]), min(current[1], other[1]),
                           max(current[2], other[2]), max(current[3], other[3])]
                spaces.pop(i)
                spaces.insert(0, current)  # Recheck this space
                break
        else:  # No merge occurred
            merged.append(current)
    return merged

def is_close(space1, space2, threshold):
    # Check horizontal and vertical proximity
    close_horizontally = space1[2] >= space2[0] - threshold or space2[2] >= space1[0] - threshold
    close_vertically = space1[3] >= space2[1] - threshold or space2[3] >= space1[1] - threshold
    return close_horizontally and close_vertically

# Rest of your code...







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
        if len(approx) >= 4:
            x, y, w, h = cv2.boundingRect(approx)
            new_panel = (x, y, x + w, y + h)

            # Check if the contour is close to a rectangle
            if area / (w * h) > 0.8:
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
def extract_panels(image_path, path_to_save_panels=""):
    if image_path.endswith(".jpg") or image_path.endswith(".png") or image_path.endswith(".jpeg") or image_path.endswith(".JPG") :
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        min_area = (width * height) * 0.1  # Minimum area threshold for an empty space

        panels = find_contours(image_path)
        empty_spaces = find_empty_spaces(image, panels)

        all_areas = panels + empty_spaces  # Combine the found panels and empty spaces

        # Sort all areas left-to-right, top-to-bottom
        all_areas.sort(key=lambda x: (x[1], x[0]))

        # Extract and save the images of all areas
        if not os.path.exists(path_to_save_panels):
            os.makedirs(path_to_save_panels)

        extracted_panels = []
        with Image.open(image_path) as img:
            for i, (x1, y1, x2, y2) in enumerate(all_areas):
                panel_image = img.crop((x1, y1, x2, y2))
                panel_path = os.path.join(path_to_save_panels, f"panel_{i+1}.png")
                panel_image.save(panel_path)
                extracted_panels.append(panel_path)

        return extracted_panels
    return None

print(get_all_file_paths("invincible"))
image_path = 'avengers_test.jpg'
panels = find_contours(image_path)
extracted_panels = extract_panels(image_path, "panels_"+image_path.split('.')[0] + "_panels/")
print(len(extracted_panels))


# Example usage with a list of Image objects
images = [display_image_with_tkinter(image_path) for image_path in extracted_panels]






# for image_path in get_all_file_paths("invincible"):
#     extracted_panels = extract_panels(image_path, "panels_"+image_path.split('.')[0] + "_panels/")
#     # print(len(extracted_panels))
#     # # Example usage with a list of Image objects
#     # images = [display_image_with_tkinter(image_path) for image_path in extracted_panels]