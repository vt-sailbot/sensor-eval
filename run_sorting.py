from data_sorter import DataSorter
import sys


def main(base_path):
    sorter = DataSorter(base_path)
    sorter.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format: " + sys.argv[0] + " <path_to_test_dataset>")
        sys.exit()
    else:
        main(sys.argv[1])