import cv2
import numpy as np
from PIL import Image
from PIL import Image, ImageTk
import tkinter as tk

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
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply a Gaussian blur to the image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Detect edges in the image
    edges = cv2.Canny(blurred, 75, 200)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # This will be a list of coordinates for the panels
    panels = []
    for contour in contours:
        # Approximate the contour to a polygon
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        # If the approximated contour has four points, we assume it's a panel (or similar shape)
        if len(approx) == 4:
            # Compute the bounding box of the contour
            (x, y, w, h) = cv2.boundingRect(approx)
            panels.append((x, y, x + w, y + h))

    return panels

def extract_panels(image_path, panels):
    with Image.open(image_path) as img:
        extracted_panels = []
        for i, (x, y, w, h) in enumerate(panels):
            panel_image = img.crop((x, y, w, h))
            panel_path = f"panel_{i+1}.png"
            panel_image.save(panel_path)
            extracted_panels.append(panel_path)
        return extracted_panels

# Usage
image_path = 'invincible/Invincible_V1-Zone-009.jpg'
panels = find_contours(image_path)
extracted_panels = extract_panels(image_path, panels)
print(len(extracted_panels))


# Example usage with a list of Image objects
images = [display_image_with_tkinter(image_path) for image_path in extracted_panels]
