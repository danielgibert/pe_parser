import unittest
from pe_parser.hexadecimal_parser import HexParser
import numpy as np

class HexadecimalParserTestCase(unittest.TestCase):
    def setUp(self):
        filepath = "test_data/0A32eTdBKayjCWhZqDOQ.bytes"
        self.hexadecimal_parser = HexParser(filepath)

    def test_extract_hex_values(self):
        hex_values = self.hexadecimal_parser.extract_hex_values()
        self.assertEqual(1201664, len(hex_values))

    def test_convert_hex_values_to_int(self):
        hex_values = self.hexadecimal_parser.extract_hex_values()
        int_values = self.hexadecimal_parser.convert_hex_values_to_int(preprocess=False,hex_values=hex_values)
        for int_value in int_values:
            self.assertEqual(type(1), type(int_value))
        int_values = self.hexadecimal_parser.convert_hex_values_to_int(preprocess=True, hex_values=hex_values)
        for int_value in int_values:
            self.assertEqual(type(1), type(int_value))

    def test_extract_byte_metadata_features(self):
        metadata_features = self.hexadecimal_parser.extract_byte_metadata_features()
        self.assertEqual(4356052, metadata_features["BYTE_MD_FileSize"])
        self.assertEqual(4198400, metadata_features["Byte_MD_FirstBytes"])

    def test_extract_byte_unigram_features(self):
        hex_values = self.hexadecimal_parser.extract_hex_values()
        unigram_features = self.hexadecimal_parser.extract_byte_unigram_features(hex_values)
        self.assertEqual(69044, unigram_features["BYTE_1GRAM_00"])
        self.assertEqual(26559, unigram_features["BYTE_1GRAM_01"])
        self.assertEqual(25602, unigram_features["BYTE_1GRAM_02"])
        self.assertEqual(26567, unigram_features["BYTE_1GRAM_03"])

    def test_extract_entropy_features(self):
        hex_values = self.hexadecimal_parser.extract_hex_values()
        entropy_features = self.hexadecimal_parser.extract_entropy_features(hex_values=hex_values)
        np.testing.assert_almost_equal(4.9856515, entropy_features["BYTE_ENT_mean"], decimal=7)
        np.testing.assert_almost_equal(6.937705, entropy_features["BYTE_ENT_variance"], decimal=6)
        np.testing.assert_almost_equal(6.477834, entropy_features["BYTE_ENT_median"], decimal=6)
        np.testing.assert_almost_equal(7.674948, entropy_features["BYTE_ENT_max"], decimal=6)
        np.testing.assert_almost_equal(0.0, entropy_features["BYTE_ENT_min"], decimal=2)
        np.testing.assert_almost_equal(0.0, entropy_features["BYTE_ENT_Quantile_1th"], decimal=2)

    def test_extract_haralick_features(self):
        grayscale_img = self.hexadecimal_parser.convert_hex_values_to_img()
        haralick_features = self.hexadecimal_parser.calculate_haralick_features(grayscale_img)
        np.testing.assert_almost_equal(0.039038908, haralick_features["BYTE_IMG_Haralick_f0"], decimal=6)
        np.testing.assert_almost_equal(11340.7069023, haralick_features["BYTE_IMG_Haralick_f1"], decimal=6)
        np.testing.assert_almost_equal(0.23196502336, haralick_features["BYTE_IMG_Haralick_f2"], decimal=6)

    def test_extract_lbp_features(self):
        grayscale_img = self.hexadecimal_parser.convert_hex_values_to_img()
        lbp_features = self.hexadecimal_parser.calculate_LBP_features(grayscale_img)
        np.testing.assert_almost_equal(310371.0, lbp_features["BYTE_IMG_lbp_f0"], decimal=1)
        np.testing.assert_almost_equal(106889.0, lbp_features["BYTE_IMG_lbp_f1"], decimal=2)
        np.testing.assert_almost_equal(8126.0, lbp_features["BYTE_IMG_lbp_f2"], decimal=2)
