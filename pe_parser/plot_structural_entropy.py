import argparse
from pe_parser.hexadecimal_parser import HexParser
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hex_filepath", type=str, help="Hexadecimal filepath")
    parser.add_argument("output_filepath", type=str, help="Output filepath")

    parser.add_argument("--chunk_size", type=int, help="Chunk size", default=256)
    args = parser.parse_args()

    hex_parser = HexParser(args.hex_filepath)
    hex_values = hex_parser.extract_hex_values()
    int_values = hex_parser.convert_hex_values_to_int(hex_values=hex_values)
    structural_entropy = hex_parser.extract_structural_entropy(int_values, chunk_size=args.chunk_size)
    print(structural_entropy)

    plt.plot(structural_entropy)
    plt.ylabel('Entropy')
    plt.xlabel('Chunk size')
    plt.savefig(args.output_filepath)
