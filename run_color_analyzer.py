import color_analyzer
import sys


def main(path):
    ca = color_analyzer.ColorAnalyzer(path, save_differences=True)
    ca.run()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format: " + sys.argv[0] + " <base_path>")
        sys.exit()
    main(sys.argv[1])
