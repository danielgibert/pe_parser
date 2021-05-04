import os
import numpy as np
import nltk
import collections
import sys
import math
import mahotas
sys.path.append("../")


class HexParser:
    def __init__(self, hex_filepath: str):
        """
        Constructor method

        Parameters
        ----------
         hex_filepath: str
             Filepath of the hexadecimal file
        """
        if not os.path.isfile(hex_filepath):
            raise IOError
        self.hex_filepath = hex_filepath

        # processed values
        self.hex_values = None
        self.int_values = None
        self.structural_entropy = None
        self.grayscale_img = None
        self.metadata = None
        self.byte_unigram_features = None
        self.entropy_features = None
        self.haralick_features = None
        self.lbp_features = None


    def extract_hex_values(self) -> list:
        """
        It returns a list of the hexadecimal values that compose the hexadecimal representation of a binary file.
        Hexadecimal values range from [0, FF]+'?' and '??'.

        Return
        ------
            hex_values: list
                List of hexadecimal values
        """
        hex_values = []
        with open(self.hex_filepath) as hex_file:
            #Extract hex values
            for line in hex_file.readlines():
                line_values = line.split()
                if len(line_values) != 17:
                    continue
                hex_values.extend(hex_value for hex_value in line_values[1:])
        self.hex_values = hex_values
        return hex_values

    def convert_hex_values_to_int(self, preprocess=False, hex_values=None):
        """
        Converts the hexadecimal values to integers. If preprocess is True, the '??' values are converted to 256.
        Otherwise, they are removed from the sequence.

        Parameters
        ----------
            preprocess: bool
                Whether or not to remove '??'
            hex_values: list
                List of hexadecimal values

        Return
        ---------
            int_values: list
                List of hexadecimal values converted to int [0,255]
        """
        if hex_values is None:
            hex_values = self.hex_values
        if preprocess:
            int_values = [int(hex_value, 16) if hex_value != '??' else 256 for hex_value in hex_values]
        else:
            int_values = [int(hex_value, 16) for hex_value in hex_values if hex_value != '??']
        self.int_values = int_values
        return int_values

    def extract_byte_metadata_features(self):
        """
        Extracts metadata information. That is, the size of the file, and the address of the firstbytes sequence.
        The address is an hexadecimal number, and we converted it to the corresponding decimalvalue for homogeneity
        with the other features values.

        Return
        ---------
            metadata: collections.OrderedDict()
                Dictionary of features
        """
        metadata = collections.OrderedDict()
        statinfo = os.stat(self.hex_filepath)
        fileSize = statinfo.st_size
        metadata["BYTE_MD_FileSize"] = fileSize

        # StartAddress
        with open(self.hex_filepath, "r") as hex_file:
            first_line = hex_file.readline().split()
            offset = first_line[0]
            dec = int(offset, 16)
            metadata["Byte_MD_FirstBytes"] = dec
        self.metadata = metadata
        return metadata

    def extract_byte_unigram_features(self, hex_values=None):
        """
        Extract unigram features

        Parameters
        ----------
            hex_values: list
                List of hexadecimal values

        Return
        ---------
            unigram_features: collections.OrderedDict()
                Dictionary of features
        """
        if hex_values is None:
            hex_values = self.hex_values
        unigram_features = collections.OrderedDict()
        fdist = nltk.FreqDist([hex_value for hex_value in hex_values if hex_value != '??'])

        # Ensure that all bytes are counter including those not appearing in the hex values sequence
        for i in range(0, 17):
            hex_value = "0{}".format(hex(i)[-1]).upper()
            try:
                unigram_features["BYTE_1GRAM_{}".format(hex_value)] = fdist[hex_value]
            except KeyError as ke:
                unigram_features["BYTE_1GRAM_{}".format(hex_value)] = 0

        for i in range(17, 256):
            hex_value = str(hex(i)[-2:]).upper()
            try:
                unigram_features["BYTE_1GRAM_{}".format(hex_value)] = fdist[hex_value]
            except KeyError as ke:
                unigram_features["BYTE_1GRAM_{}".format(hex_value)] = 0
        self.byte_unigram_features = unigram_features
        return unigram_features

    def extract_entropy_features(self, hex_values=None, chunk_size=1024):
        """
        Calculates percentiles, mean, variance, median, max, min

        Return
        ---------
            unigram_features: collections.OrderedDict()
                Dictionary of features
        """
        entropy_features = collections.OrderedDict()
        if hex_values is None:
            hex_values = self.hex_values

        hex_values_preprocessed = [int(hex_value, 16) if hex_value != '??' else 256 for hex_value in hex_values]
        structural_entropy = self.extract_structural_entropy(hex_values_preprocessed, chunk_size=chunk_size, log=2)
        mean = np.mean(structural_entropy)
        variance = np.var(structural_entropy)
        median = np.median(structural_entropy)
        max = np.max(structural_entropy)
        min = np.min(structural_entropy)
        entropy_features["BYTE_ENT_mean"] = mean
        entropy_features["BYTE_ENT_variance"] = variance
        entropy_features["BYTE_ENT_median"] = median
        entropy_features["BYTE_ENT_max"] = max
        entropy_features["BYTE_ENT_min"] = min


        for i in range(1,101):
            q = i / 100
            qth = np.quantile(structural_entropy, q)
            entropy_features["BYTE_ENT_Quantile_{}th".format(int(q*100))] = qth
        self.entropy_features = entropy_features
        return entropy_features

    def extract_structural_entropy(self, hex_values, chunk_size=256, log=2):
        """
        Split the file into non-overlapping chunks of fixed size. For each chunk, calculate the entropy.

        Parameters
        ----------
        chunk_size: int
            Number of hex values per chunk

        Return
        ------
        structural_entropy: list
            The entropy of every non-overlapping chunk
        """
        structural_entropy = []
        print("Len bytes: {}".format(len(hex_values)))
        num_chunks = int(len(hex_values) / chunk_size)
        for i in range(num_chunks):
            chunk = hex_values[i * chunk_size:(i + 1) * chunk_size]
            len_chunk = float(len(chunk))
            counts = np.bincount(chunk)
            probs = counts / len_chunk
            entropy = sum([-p * math.log(p, log) if p > 0 else 0 for p in probs])
            structural_entropy.append(entropy)

        print("Reached here: {}".format(len(structural_entropy)))
        structural_entropy = np.array(structural_entropy, dtype=np.float32)
        self.structural_entropy = structural_entropy
        return structural_entropy

    def convert_hex_values_to_img(self):
        """

        :param hex_values: list of hexadecimal values
        :return:
        """
        import subprocess
        #print(os.path.dirname(os.path.abspath(__file__)))
        script = ["python2",
                  "{}/py2_generate_grayscale_img.py".format(os.path.dirname(os.path.abspath(__file__))),
                  "{}".format(self.hex_filepath)]
        process = subprocess.Popen(script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        content = out.decode("utf-8").split("\n")
        img_content = np.array([int(x) for x in content[:-3]])

        a = int(content[-3])
        b = int(content[-2])
        grayscale_img = np.reshape(img_content, (a, b))
        self.grayscale_img = grayscale_img
        return grayscale_img

    def calculate_haralick_features(self, grayscale_img: np.array):
        """
        Calculate Haralick features from a grayscale image

        Parameters
        ----------
            grayscale_img: np.array
                Grayscale image of the file

        Return
        ---------
            haralick_features: collections.OrderedDict()
                Dictionary of features
        """
        haralick_features = collections.OrderedDict()
        h_features = mahotas.features.haralick(grayscale_img)
        k = 0
        for i in range(len(h_features)):
            for j in range(len(h_features[0])):
                haralick_features["BYTE_IMG_Haralick_f{}".format(k)] = h_features[i][j]
                k += 1
        self.haralick_features = haralick_features
        return haralick_features

    def calculate_LBP_features(self, grayscale_img: np.array):
        """
        Calculate Local Binary Pattern features from a grayscale image

        Parameters
        ----------
            grayscale_img: np.array
                Grayscale image of the file

        Return
        ---------
            haralick_features: collections.OrderedDict()
                Dictionary of features
        """
        lbp_features = collections.OrderedDict()
        lbp_points = mahotas.features.lbp(grayscale_img, 10, 10, ignore_zeros=False)
        for i in range(len(lbp_points.tolist())):
            lbp_features["BYTE_IMG_lbp_f{}".format(i)] = lbp_points.tolist()[i]
        self.lbp_features = lbp_features
        return lbp_features

    def extract_ngrams_freq(self, tokens, n):
        tgs = nltk.ngrams(tokens, n)
        fdist = nltk.FreqDist(tgs)
        return fdist

    def extract_ngram_features(self, N:int):
        """

        :param N:
        :param opcodes:
        :return:
        """
        hex_values = self.extract_hex_values()
        fdist = self.extract_ngrams_freq(hex_values, N)
        return fdist








