from image_truther import ImageTruther
import sys


def main(path, closeup_radius):
    truther = ImageTruther(path, closeup_radius)
    truther.run()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Format: " + sys.argv[0] + " <path_to_test_dataset_directory> <closeup_radius>")
        sys.exit()
    else:
        main(sys.argv[1], int(sys.argv[2]))
