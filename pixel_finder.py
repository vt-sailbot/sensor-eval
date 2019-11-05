"""
pixel_finder.py
Evan Allen - SailBOT Buoy Detection 2019-2020
Adapted from Wyatt Lansford's test_cameras.py in the sailbot-20 repo.

Tool to evaluate our current buoy detection capabilities.
This tool will:
(1) Look in [BASE_PATH]/BUOY_PRESENT/ for buoy images, and display them one at a time with the buoy pixels
    highlighted.

Current buoy detection methods:
- Color matching
"""

import os
import sys
import cv2
import numpy as np
import pickle


class PixelFinder:
    def __init__(self, base_path, hsv_low, hsv_high, threshold):
        self.BASE_PATH = base_path
        self.IMG_PATH = self.BASE_PATH + "/BUOY_PRESENT/"
        self.HSV_LOW = hsv_low
        self.HSV_HIGH = hsv_high
        self.image_names = []
        self.current_img_index = 0
        self.current_filename = None
        self.kernel_open = np.ones((2, 2))
        self.kernel_close = np.ones((12, 12))
        self.threshold = threshold
        self.histograms = None

    def run(self):
        if not self.check_directories():
            sys.exit()

        self.get_image_names()

        self.show_images()

    def check_directories(self):
        """
        Ensure that ./TEST_DATASET directory exists and that ./TEST_DATASET/BUOY_PRESENT exists.
        :return: False if a fatal error is encountered, or True otherwise.
        """
        if not os.path.isdir(self.BASE_PATH):
            print("FATAL ERROR: [file_path]/TEST_DATASET/ doesn't exist. Create it first and load some " +
                  "images in with the single_camera_image_capture.py script, and then classify them with " +
                  "data_sorter.py.")
            return False

        if not os.path.isdir(self.IMG_PATH):
            print(
                "FATAL ERROR: [file_path]/TEST_DATASET/BUOY_PRESENT/ doesn't exist. Run data_sorter.py on the images " +
                "you've collected with the single_camera_image_capture.py script, and then run this.")
            return False

        return True

    def get_image_names(self):
        """
        Get the image names in the IMG_PATH directory.
        """
        self.image_names = sorted([os.path.basename(name) for name in os.listdir(self.IMG_PATH)])

    def show_images(self):
        """
        Show each image in the BUOY_PRESENT directory with the identified buoy pixels highlighted using a red
        contour.
        Use `j` to move to the next image, and `k` to move to the previous one.
        """
        self.current_filename = self.image_names[self.current_img_index]
        while True:
            print("Current file: " + self.IMG_PATH + self.current_filename)
            image = cv2.imread(self.IMG_PATH + self.current_filename)
            self.process_image(image)
            cv2.imshow("Image", image)

            valid_key_pressed = False
            while not valid_key_pressed:
                key = cv2.waitKey(0)
                valid_key_pressed = self.handle_keycode(key)

    def handle_keycode(self, key):
        """
        Responds appropriately to a keystroke, switching to the next/previous image (if there is one) or quitting
        depending on the keypress.
        :param key: The CV2 keycode of the key pressed.
        :return: True if a valid key was pressed, and False otherwise.
        """
        # Next image, if there is one
        if key == ord('j'):
            if self.current_img_index < len(self.image_names) - 1:
                self.current_img_index += 1
                self.current_filename = self.image_names[self.current_img_index]
            return True

        # Previous image, if there is one
        elif key == ord('k'):
            if self.current_img_index > 0:
                self.current_img_index -= 1
                self.current_filename = self.image_names[self.current_img_index]
            return True

        # Quit
        elif key == ord('q'):
            sys.exit()

        return False

    def process_image(self, image):
        """
        Convert the image to HSV, find the buoy-colored pixels, and draw contours.
        :param image: The image to analyze.
        """
        # Convert image to HSV, and find/clean mask with buoy-colored pixels.
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        self.get_histogram()

        cv2.imshow("image", image)

        relevance_map = self.get_relevance_map(hsv)
        cv2.imshow("relevance_map", relevance_map)

        _, mask = cv2.threshold(relevance_map, self.threshold, 255, cv2.THRESH_BINARY)
        mask = self.clean_mask(mask)

        cv2.imshow("mask", mask)

        # Draw contours on the image based on the mask.
        # contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(image, contours, -1, (0, 0, 255), 1)

    def clean_mask(self, mask):
        """
        Execute opening/closing operations on the mask to get rid of small holes / specks in it.
        :param mask: The mask to clean.
        :return: The cleaned mask.
        """
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel_open)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel_close)
        return mask

    def get_relevance_map(self, hsv):

        def map_func(depth_channels):
            hue_hist = self.histograms[0]
            sat_hist = self.histograms[1]
            val_hist = self.histograms[2]

            return hue_hist[depth_channels[0]] + sat_hist[depth_channels[1]] + val_hist[depth_channels[2]]

        relevance_map = np.apply_along_axis(map_func, 2, hsv)
        cv2.normalize(relevance_map, relevance_map, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        relevance_map = relevance_map.astype(np.uint8)
        # Denoise
        relevance_map = cv2.medianBlur(relevance_map, 7)

        return relevance_map

    def get_histogram(self):
        with open("buoy_histogram.pickle", "rb") as pickle_file:
            self.histograms = pickle.load(pickle_file)
