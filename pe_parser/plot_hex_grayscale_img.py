import argparse
from pe_parser.hexadecimal_parser import HexParser
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hex_filepath", type=str, help="Hexadecimal filepath")
    parser.add_argument("output_filepath", type=str, help="Output filepath")
    args = parser.parse_args()

    hex_parser = HexParser(args.hex_filepath)
    grayscale_img = hex_parser.convert_hex_values_to_img()
    plt.imshow(grayscale_img, cmap='gray', vmin=0, vmax=255)
    plt.savefig(args.output_filepath)

