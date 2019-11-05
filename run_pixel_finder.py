import pixel_finder
import sys
import numpy as np


def main(base_path, hsv_low, hsv_high, threshold):
    pf = pixel_finder.PixelFinder(base_path, hsv_low, hsv_high, threshold)
    pf.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format: " + sys.argv[0] + " <base_path>")
        sys.exit()

    HSV_LOW = np.array([1, 50, 30], np.uint8)
    HSV_HIGH = np.array([36, 255, 255], np.uint8)
    THRESHOLD_PCT = 0.8

    path = sys.argv[1]
    main(path, HSV_LOW, HSV_HIGH, THRESHOLD_PCT * 255)
