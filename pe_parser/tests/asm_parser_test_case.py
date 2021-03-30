import unittest
from pe_parser.asm_parser import AssemblyParser


class AssemblyParserTestCase(unittest.TestCase):
    def setUp(self):
        filepath = "test_data/0A32eTdBKayjCWhZqDOQ.asm"
        self.asm_parser = AssemblyParser(filepath)

    def test_extract_assembly_language_source_code(self):
        source_code = self.asm_parser.extract_assembly_language_source_code()
        self.assertIsNotNone(source_code.x86_instructions)

    def test_extract_metadata_features(self):
        metadata_features = self.asm_parser.extract_asm_metadata_features()
        self.assertEqual(38495501, metadata_features["ASM_MD_FileSize"])
        self.assertEqual(896510, metadata_features["ASM_MD_NumLines"])

    def test_extract_symbol_features(self):
        symbol_features = self.asm_parser.extract_symbol_features()
        self.assertEqual(2040, symbol_features["ASM_SYMBOLS_*"])
        self.assertEqual(3742, symbol_features["ASM_SYMBOLS_-"])
        self.assertEqual(6624, symbol_features["ASM_SYMBOLS_+"])
        self.assertEqual(4414, symbol_features["ASM_SYMBOLS_left_bracket"])

    def test_extract_opcode_unigram_features(self):
        opcode_features = self.asm_parser.extract_opcode_unigram_features()
        self.assertEqual(194, opcode_features["ASM_1GRAM_OPCODES_add"])
        self.assertEqual(187, opcode_features["ASM_1GRAM_OPCODES_al"])
        self.assertEqual(0, opcode_features["ASM_1GRAM_OPCODES_bt"])
        self.assertEqual(411, opcode_features["ASM_1GRAM_OPCODES_call"])

    def test_extract_register_features(self):
        register_features = self.asm_parser.extract_register_features()
        self.assertEqual(0, register_features["ASM_REG_rax"])
        self.assertEqual(1046, register_features["ASM_REG_eax"])
        self.assertEqual(4, register_features["ASM_REG_ax"])

    def test_extract_API_features(self):
        api_features = self.asm_parser.extract_API_features()
        self.assertEqual(0, api_features["ASM_API_wcslen"])
        self.assertEqual(7, api_features["ASM_API__XcptFilter"])
        self.assertEqual(4, api_features["ASM_API_GetUserDefaultLCID"])

    def test_extract_MISC_features(self):
        misc_features = self.asm_parser.extract_MISC_features()
        self.assertEqual(32, misc_features["ASM_MISC_Virtual"])
        self.assertEqual(168, misc_features["ASM_MISC_Offset"])
        self.assertEqual(2697, misc_features["ASM_MISC_loc"])

    def test_extract_section_features(self):
        section_features = self.asm_parser.extract_section_features()
        self.assertEqual(13801, section_features["ASM_SECTION_.text"])
        self.assertEqual(842632, section_features["ASM_SECTION_.data"])
        self.assertEqual(0, section_features["ASM_SECTION_.bss"])

    def test_extract_data_define_features(self):
        data_define_features = self.asm_parser.extract_data_define_features()
        self.assertEqual(6, data_define_features["ASM_DD_dd5"])
        self.assertEqual(0, data_define_features["ASM_DD_dd4"])

    def test_extract_pixel_intensity_features(self):
        asm_img = self.asm_parser.convert_asm_to_img()
        pixel_intensities = self.asm_parser.extract_pixel_intensities(num_pixels=800, asm_img=asm_img)
        self.assertEqual(46, pixel_intensities["ASM_PIXEL_0th"])
        self.assertEqual(116, pixel_intensities["ASM_PIXEL_1th"])
        self.assertEqual(101, pixel_intensities["ASM_PIXEL_2th"])
