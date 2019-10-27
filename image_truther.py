"""image_truther.py
Evan Allen - SailBOT Buoy Detection 2019-2020

This script is meant act as a tool for users to identify which pixels in collected test images contain buoys.
All images with the buoys should be placed in ./TEST_DATASET/BUOY_PRESENT.

For each image in that directory, this script will display it to the user and allow them to draw a circle on the
image to identify the buoy (by:
    [1] clicking on the center of the buoy, and
    [2] dragging out the radius to the edge of the buoy).

To modify a given circle, a user can:
    - Drag out a new circle
    - Use the h/j/k/l keys to move the circle left/down/up/right, respectively (VIM bindings)
    - Use the n/m keys to make the circle smaller/larger, respectively.

Once a circle is selected, the user will press a CONFIRM key (here: [space]) that will prompt the program to
save an image file to BUOY_MASK_IMAGES under the format `mask.[original_image_name_and_extension]`.
Each mask will contain white pixels in the circle selected by the user, and black pixels everywhere else.

Ex. 2019-11-14_10-40_43.png -> mask.2019-11-14_10-40_43.png
"""

import cv2
import os
import sys
import math
import numpy as np


class ImageTruther:

    def __init__(self, base_path, closeup_radius):
        self.BASE_PATH = base_path
        self.SRC_IMAGE_PATH = self.BASE_PATH + "BUOY_PRESENT/"
        self.MASK_PATH = self.BASE_PATH + "BUOY_MASK_IMAGES/"
        self.SAVE_FILE_PATH = self.BASE_PATH + "save_file.txt"

        self.CLOSEUP_RADIUS = closeup_radius
        self.buoy_center = None
        self.buoy_radius = 0
        self.mouse_dragging = False
        self.mouse_pos = (0, 0)

    def run(self):
        # Set up.
        if not self.check_directories():
            sys.exit()
        last_image = self.load_savefile()
        self.setup_windows()

        # Iterate through all the images in ./TEST_DATASET/BUOY_PRESENT, displaying them each to the user.
        image_names = [os.path.basename(name) for name in os.listdir(self.SRC_IMAGE_PATH)]
        image_names = sorted(image_names)

        # Skip to where we left off if we're resuming from a previous save.
        if last_image is not None:
            index = image_names.index(last_image)
            image_names = image_names[index:]

        # Go through each image, allowing the user to mark the parts containing a buoy.
        self.iterate_images(image_names)

    def check_directories(self):
        """
        Ensure that ./TEST_DATASET directory exists and that ./TEST_DATASET/BUOY_PRESENT exists.
        :return: False if a fatal error is encountered or the user elects to quit, or True otherwise.
        """
        if not os.path.isdir(self.BASE_PATH):
            print("FATAL ERROR: [file_path]/TEST_DATASET/ doesn't exist. Create it first and load some " +
                  "images in with the single_camera_image_capture.py script, and then classify them with " +
                  "data_sorter.py.")
            return False

        if not os.path.isdir(self.SRC_IMAGE_PATH):
            print("FATAL ERROR: [file_path]/TEST_DATASET/BUOY_PRESENT/ doesn't exist. Run data_sorter.py on the images " +
                  "you've collected with the single_camera_image_capture.py script, and then run this.")
            return False

        # Check if the ./TEST_DATASET/BUOY_MASK_IMAGES directory exists.
        # If it doesn't, make it.
        # If it does, make sure the user wants to continue.
        if not os.path.isdir(self.MASK_PATH):
            print("Creating " + self.MASK_PATH + " directory.")
            os.mkdir(self.MASK_PATH)
        else:
            response = input(self.MASK_PATH + " directory already exists. Continue? (y/N): ")
            if not (response == 'y' or response == 'Y'):
                return False

        return True

    def load_savefile(self):
        """
        Checks to see if we have a save file - i.e., if we ran this program before and stopped at a certain picture.
        If we have, it fetches the name of that picture and returns it.

        :return: The name of the last picture we left off on if there is a save file (and we want to use it),
        or None otherwise.
        """
        # Check if there's a saved file, and ask if we want to resume from there.
        if os.path.exists(self.SAVE_FILE_PATH):
            file = open(self.SAVE_FILE_PATH, 'r')
            file_contents = file.readline()
            response = input("Previous save file found. Save from " + file_contents + "? (Y/n): ")
            if not (response == 'n' or response == 'N'):
                return file_contents
            os.remove(self.SAVE_FILE_PATH)

        return None

    def setup_windows(self):
        """
        Set up the CV2 windows - one ("image") for the main image being displayed, and another ("closeup") for a
        detailed view of the image where the cursor is (to aid when marking small objects).
        """
        # Set up the CV2 window.
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", self.mouse_callback)

        # This window helps see a closeup of the mouse cursor.
        cv2.namedWindow("closeup")

    def iterate_images(self, image_names):
        """
        Iterate through each image, (1) displaying it on the screen, (2) allowing the user to select a region as the buoy,
        and (3) allowing the user to save that region as a mask.
        :param image_names: The names of all the images to iterate through as a list of strings.
        """

        for image_name in image_names:

            # Get the image, and reset all the mouse / buoy values.
            original_img = cv2.imread(self.SRC_IMAGE_PATH + image_name)
            img_height = original_img.shape[0]
            img_width = original_img.shape[1]

            cv2.putText(original_img, image_name, (5, img_height - 5), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
            img = original_img.copy()
            self.buoy_center = None
            self.buoy_radius = 0
            self.mouse_dragging = False

            # Wait for user input, and redraw any annotations the user makes.
            while True:
                cv2.imshow('image', img)
                img = original_img.copy()

                key_code = cv2.waitKey(1)
                if self.handle_keycode(key_code, image_name, img_width, img_height):
                    break

                # Draw the buoy's bounding circle & center of mass.
                circle_color = (0, 0, 255)  # Blue, Green, Red
                if self.buoy_center is not None:
                    cv2.circle(img, tuple(self.buoy_center), self.buoy_radius, circle_color)

                self.display_closeup_window(img, img_width, img_height)

    def mouse_callback(self, event, x, y, flags, params):

        if event == cv2.EVENT_LBUTTONDOWN:
            # Set new buoy_center
            self.buoy_center = [x, y]
            self.mouse_dragging = True
            self.buoy_radius = 0

        elif event == cv2.EVENT_LBUTTONUP:
            self.mouse_dragging = False

        elif event == cv2.EVENT_MOUSEMOVE:
            self.mouse_pos = (x, y)
            if self.mouse_dragging:
                # Find distance between the buoy_center and the mouse's current location. That's the new radius!
                displacement_vector = (x - self.buoy_center[0], y - self.buoy_center[1])
                self.buoy_radius = int(math.sqrt(displacement_vector[0] ** 2 + displacement_vector[1] ** 2))

    def save_img_mask(self, img_width, img_height, img_name):
        """
        Save an image mask corresponding to the selected region.
        Everything in the image mask will be black (value: 0) except for the selected region, which will be white
        (value: 255). The image has one layer of depth only.
        :param buoy_center: The center of the buoy in image coordinates.
        :param buoy_radius: The radius of the buoy in image coordinates.
        :param img_width: The width of the image.
        :param img_height: The height of the image.
        :param img_name: The name of the image (so we can make a similar-sounding mask image name).
        """
        mask = np.zeros((img_height, img_width, 1), np.uint8)
        cv2.circle(mask, tuple(self.buoy_center), self.buoy_radius, (255,), thickness=-1)
        cv2.imwrite(self.MASK_PATH + "mask." + img_name, mask)

    def display_closeup_window(self, img, img_width, img_height):
        closeup_x1 = max(0, self.mouse_pos[0] - self.CLOSEUP_RADIUS)
        closeup_x2 = min(img_width - 1, self.mouse_pos[0] + self.CLOSEUP_RADIUS)
        closeup_y1 = max(0, self.mouse_pos[1] - self.CLOSEUP_RADIUS)
        closeup_y2 = min(img_height - 1, self.mouse_pos[1] + self.CLOSEUP_RADIUS)
        closeup_img = img[closeup_y1:closeup_y2, closeup_x1:closeup_x2].copy()

        cv2.line(closeup_img, (self.CLOSEUP_RADIUS, 0), (self.CLOSEUP_RADIUS, 2 * self.CLOSEUP_RADIUS), (0, 0, 255))
        cv2.line(closeup_img, (0, self.CLOSEUP_RADIUS), (2 * self.CLOSEUP_RADIUS, self.CLOSEUP_RADIUS), (0, 0, 255))

        cv2.imshow("closeup", closeup_img)

    def handle_keycode(self, keycode, img_name, img_width, img_height):
        """Does appropriate behavior depending on what key is pressed.
        Returns True if the space key was pressed (and we want to save the mask and move on), or False if
        any other key was pressed.
        """

        if keycode == ord('q'):
            self.save_and_quit(img_name)
        elif keycode == ord(' '):
            print("Saving file!")
            self.save_img_mask(img_width, img_height, img_name)
            return True
        elif keycode == ord('h'):
            self.buoy_center[0] -= 1  # Move the buoy center LEFT one.
        elif keycode == ord('l'):
            self.buoy_center[0] += 1  # Move the buoy center RIGHT one.
        elif keycode == ord('j'):
            self.buoy_center[1] += 1  # Move the buoy center DOWN one.
        elif keycode == ord('k'):
            self.buoy_center[1] -= 1  # Move the buoy center UP one.
        elif keycode == ord('m'):
            self.buoy_radius += 1  # Expand the buoy radius by one.
        elif keycode == ord('n'):
            self.buoy_radius = max(0, self.buoy_radius - 1)  # Decrease the buoy radius by one.

        return False

    def save_and_quit(self, img_name):
        """
        Create a save file (or overwrite one if it exists) that contains the name of the image we're currently working
        on.
        :param img_name: The name of the image we're currently working on.
        """
        file = open(self.SAVE_FILE_PATH, 'w')
        file.write(img_name)
        sys.exit()