import math
import numpy as np
import argparse

def convert_hex_values_to_img_python2(hex_filepath):
    """
    Converts the hexadecimal values representing an executable's binary content into a grayscale image.

    Parameters
    ----------
    hex_filepath: str
        Filepath containing the hexadecimal representation of the executable's binary content.
    """
    with open(hex_filepath) as hex_file:
        # Extract hex values
        hex_array = []
        for line in hex_file.readlines():
            line = line.strip()
            hex_values = line.split()
            if len(hex_values) != 17:
                continue
            hex_array.append([int(i, 16) if i != '??' else 0 for i in hex_values[1:]])
        hex_array = np.array(hex_array)

        # Convert to an image of a specific size
        if hex_array.shape[1] != 16:
            assert (False)
        b = int((hex_array.shape[0] * 16) ** (0.5))
        b = 2 ** (int(math.log(b) / math.log(2)) + 1)
        a = int(hex_array.shape[0] * 16 / b)
        hex_array = hex_array[:a * b / 16, :]
        im = np.reshape(hex_array, (a, b))
        im = im.flatten()
        for x in im:
            print(x)
        print(a)
        print(b)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("hex_filepath", help="Hexadecimal filepath", type=str)
    args = parser.parse_args()
    convert_hex_values_to_img_python2(args.hex_filepath)
