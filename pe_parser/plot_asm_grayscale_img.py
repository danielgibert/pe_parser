import argparse
from pe_parser.asm_parser import AssemblyParser
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("asm_filepath", type=str, help="Assembly filepath")
    parser.add_argument("output_filepath", type=str, help="Output filepath")
    args = parser.parse_args()

    asm_parser = AssemblyParser(args.asm_filepath)
    grayscale_img = asm_parser.convert_asm_to_img()
    plt.imshow(grayscale_img, cmap='gray', vmin=0, vmax=255)
    plt.savefig(args.output_filepath)