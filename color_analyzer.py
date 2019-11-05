import os
import sys
import cv2
from matplotlib import pyplot as plt
import mplcursors
import pickle


class ColorAnalyzer:
    def __init__(self, base_path, save_differences=False, show_all=True):
        self.BASE_PATH = base_path
        self.IMG_PATH = base_path + "/BUOY_PRESENT/"
        self.MASK_PATH = base_path + "/BUOY_MASK_IMAGES/"
        self.image_names = []
        self.current_file = None
        self.hue_hist_buoy, self.hue_hist_other = None, None
        self.sat_hist_buoy, self.sat_hist_other = None, None
        self.val_hist_buoy, self.val_hist_other = None, None
        self.total_hist_buoy, self.total_hist_other = None, None
        self.show_all = show_all
        self.save_differences = save_differences

    def run(self):
        if not self.check_directories():
            sys.exit()
        self.load_image_names()

        self.calculate_histograms()
        if self.show_all:
            self.show_histograms()
        else:
            self.show_diff_hist_only()

        if self.save_differences:
            self.create_differences_file()

    def check_directories(self):
        """
        Ensure that ./TEST_DATASET, ./TEST_DATASET/BUOY_PRESENT, and ./TEST_DATASET/BUOY_MASK_IMAGES exists.
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

        if not os.path.isdir(self.MASK_PATH):
            print(
                "FATAL ERROR: [file_path]/TEST_DATASET/BUOY_MASK_IMAGES/ doesn't exist. Run run_truthing.py on " +
                " the images in BUOY_PRESENT, and then run this."
            )
            return False

        return True

    def load_image_names(self):
        """Get the image names in the IMG_PATH directory.
        """
        self.image_names = sorted([os.path.basename(name) for name in os.listdir(self.IMG_PATH)])

    def calculate_histograms(self):
        """
        Calculate the HSV histograms from the images under IMG_PATH (using the masks in MASK_PATH).
        Calculates three sets of HSV histograms:

        (1) Buoy histograms - HSV values taken from the part of the image with the buoy (implemented by applying the
        mask).

        (2) Other histograms - HSV values taken from the part of the image without the buoy (implemented by applying
        the OPPOSITE [read: bitwise NOT] of the mask).

        (3) Difference histograms - The difference between the buoy histograms and the other histograms. Positive
        values indicate HSV values found MORE in the buoy sections than in the non-buoy sections, and vice-versa for
        negative.
        """
        for image_name in self.image_names:
            self.current_file = image_name

            image = cv2.imread(self.IMG_PATH + self.current_file)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            mask = cv2.imread(self.MASK_PATH + "mask." + self.current_file)
            mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            inverted_mask = cv2.bitwise_not(mask)

            '''
            Set `accumulate`=True so that we add up the contribution of each image; otherwise, it overwrites the 
            histogram each time.
            Set `hist` to specify which histogram we're accumulating from. 
            '''
            self.hue_hist_buoy = \
                cv2.calcHist([hsv], [0], mask, [180], [0, 179], hist=self.hue_hist_buoy, accumulate=True)
            self.sat_hist_buoy = \
                cv2.calcHist([hsv], [1], mask, [256], [0, 255], hist=self.sat_hist_buoy, accumulate=True)
            self.val_hist_buoy = \
                cv2.calcHist([hsv], [2], mask, [256], [0, 255], hist=self.val_hist_buoy, accumulate=True)

            self.hue_hist_other = \
                cv2.calcHist([hsv], [0], inverted_mask, [180], [0, 179], hist=self.hue_hist_other, accumulate=True)
            self.sat_hist_other = \
                cv2.calcHist([hsv], [1], inverted_mask, [256], [0, 255], hist=self.sat_hist_other, accumulate=True)
            self.val_hist_other = \
                cv2.calcHist([hsv], [2], inverted_mask, [256], [0, 255], hist=self.val_hist_other, accumulate=True)

        # We normalize because there are much more pixels in the non-buoy parts of the image, so those when we
        # subtract the histograms to find the difference, they'd overwhelm the buoy histograms.
        self.normalize_histograms()

    def normalize_histograms(self):
        """
        Normalize each histogram array so their values are comparable.
        """
        # Buoy histograms
        cv2.normalize(self.hue_hist_buoy, self.hue_hist_buoy)
        cv2.normalize(self.sat_hist_buoy, self.sat_hist_buoy)
        cv2.normalize(self.val_hist_buoy, self.val_hist_buoy)

        # Other histograms
        cv2.normalize(self.hue_hist_other, self.hue_hist_other)
        cv2.normalize(self.sat_hist_other, self.sat_hist_other)
        cv2.normalize(self.val_hist_other, self.val_hist_other)

    def show_histograms(self):
        """
        Display each histogram side-by-side, with the HSV histograms for each set on top of one another.
        """
        # Buoy HSV Plot
        fig, axs = plt.subplots(1, 3)
        axs[0].plot(self.hue_hist_buoy, label="Hue")
        axs[0].plot(self.sat_hist_buoy, label="Saturation")
        axs[0].plot(self.val_hist_buoy, label="Value")

        axs[0].set_xlabel("Hue / Saturation / Value")
        axs[0].set_ylabel("Frequency")
        axs[0].set_title("Total **BUOY** HSV Histogram")
        axs[0].legend()

        # Other HSV Plot (for the _rest_ of the image)
        axs[1].plot(self.hue_hist_other, label="Hue")
        axs[1].plot(self.sat_hist_other, label="Saturation")
        axs[1].plot(self.val_hist_other, label="Value")

        axs[1].set_xlabel("Hue / Saturation / Value")
        axs[1].set_ylabel("Frequency")
        axs[1].set_title("Total **OTHER** HSV Histogram")
        axs[1].legend()

        # Difference HSV Plot
        axs[2].plot(self.hue_hist_buoy - self.hue_hist_other, label="Hue")
        axs[2].plot(self.sat_hist_buoy - self.sat_hist_other, label="Saturation")
        axs[2].plot(self.val_hist_buoy - self.val_hist_other, label="Value")

        axs[2].set_xlabel("Hue / Saturation / Value")
        axs[2].set_ylabel("Difference in Frequency")
        axs[2].set_title("Difference")
        axs[2].legend()

        mplcursors.cursor()

        plt.show()

    def show_diff_hist_only(self):
        # Difference HSV Plot
        plt.plot(self.hue_hist_buoy - self.hue_hist_other, label="Hue")
        plt.plot(self.sat_hist_buoy - self.sat_hist_other, label="Saturation")
        plt.plot(self.val_hist_buoy - self.val_hist_other, label="Value")

        plt.xlabel("Hue / Saturation / Value")
        plt.ylabel("Difference in Frequency")
        plt.grid()
        plt.title("Difference")
        plt.legend()

        mplcursors.cursor()

        plt.show()

    def create_differences_file(self):
        with open("buoy_histogram.pickle", "wb") as pickle_out:
            dump_tuple = (self.hue_hist_buoy - self.hue_hist_other,
                          self.sat_hist_buoy - self.sat_hist_other,
                          self.val_hist_buoy - self.val_hist_other)
            pickle.dump(dump_tuple, pickle_out)


