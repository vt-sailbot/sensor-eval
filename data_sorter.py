"""data_sorter.py
Evan Allen - SailBOT Buoy Detection 2019-2020

Tool to help classify images into BUOY_PRESENT or BUOY_NOT_PRESENT classes.
Will iterate through all images in a subdirectory in this folder (_except
those in BUOY_PRESENT or BUOY_NOT_PRESENT subdirectories), and will display them
for the user to input 'y' (buoy _is_ present), or 'n' (buoy _isn't_ present).
Depending on the answer, the program will copy the image file (retaining information
about the date it was taken through the filename) into the proper folder and move
on to the next image.
If you are running this a second time with BUOY_PRESENT / BUOY_NOT_PRESENT directories
already created, it will prompt you before continuing, since you might be introducing
repeats.

WARNING: ./TEST_DATASET must exist in the same directory as this file before you run this program.
It will break if it doesn't.
"""

import os
import shutil
import sys

from matplotlib import image as mpimg
from matplotlib import pyplot as plt


class DataSorter:
    def __init__(self, base_path):
        self.BASE_PATH = base_path
        self.sort_decision = None

    def run(self):
        self.check_directories_exist()
        self.iterate_through_directories()

    def check_directories_exist(self):
        """
        Make sure that ./TEST_DATASET exists.
        :return:
        """
        if not os.path.isdir(self.BASE_PATH):
            print("FATAL ERROR: [file_path]/TEST_DATASET/ doesn't exist. Create it first and load some " +
                  "images in with the single_camera_image_capture.py script.")
            sys.exit()

        # Create BUOY_PRESENT and BUOY_NOT_PRESENT directories if they don't exist.
        if not os.path.exists(self.BASE_PATH + 'BUOY_PRESENT'):
            print("Making " + self.BASE_PATH + "BUOY_PRESENT directory.")
            os.mkdir(self.BASE_PATH + 'BUOY_PRESENT')
        else:
            response = input("BUOY_PRESENT directory already exists. Continue? (y/N): ")
            if response != 'y':
                sys.exit()

        if not os.path.exists(self.BASE_PATH + 'BUOY_NOT_PRESENT'):
            print("Making " + self.BASE_PATH + "BUOY_NOT_PRESENT directory.")
            os.mkdir(self.BASE_PATH + 'BUOY_NOT_PRESENT')
        else:
            response = input("BUOY_NOT_PRESENT directory already exists. Continue? (y/N): ")
            if response != 'y':
                sys.exit()

    def press_handler(self, event):
        key = event.key
        if key == 'q':
            plt.close()
            sys.exit()
        elif key == 'y':
            self.sort_decision = 'y'
            plt.close()
        elif key == 'n':
            self.sort_decision = 'n'
            plt.close()

    def iterate_through_directories(self):
        """
        Iterate through each directory.
        In each one, iterate through each image and display it to the user.
        If the user presses the 'y' key, put the image into the BUOY_PRESENT directory.
        If the user presses the 'n' key, put the image into the BUOY_NOT_PRESENT directory.
        Name it according to the date it was taken (SRC_DIRECTORY_NAME _ IMAGE_NAME)
        :return:
        """
        # Get list of source directories to sort through (but not our destination ones!)
        image_directories = [os.path.basename(name) for name in os.listdir(self.BASE_PATH)
                             if os.path.isdir(self.BASE_PATH + name) and name[:4] != 'BUOY']
        print("Image directories: " + str(image_directories))

        for directory in image_directories:
            image_names = [os.path.basename(name) for name in os.listdir(self.BASE_PATH + directory)]
            for image_name in image_names:
                # Setup the figure to display the image and connect our keypress handler.
                fig = plt.figure()
                fig.canvas.mpl_connect('key_press_event', self.press_handler)
                self.sort_decision = None

                # Display the image and wait for a keypress.
                path = self.BASE_PATH + directory + '/' + image_name
                img = mpimg.imread(path)
                plt.imshow(img)
                plt.title(path)
                plt.show()

                # Copy the image.
                if self.sort_decision == 'y':
                    shutil.copyfile(path, self.BASE_PATH + 'BUOY_PRESENT/' + directory + '_' + image_name)
                elif self.sort_decision == 'n':
                    shutil.copyfile(path, self.BASE_PATH + 'BUOY_NOT_PRESENT/' + directory + '_' + image_name)
