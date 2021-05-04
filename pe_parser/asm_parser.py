import os
import collections
import numpy as np
from pe_parser.utils import header_asm_sections, header_asm_data_define
from pe_parser.assembly_language_instructions_parser import AssemblyLanguageInstructionsParser
from pe_parser.x86_asm_intermediate_representation import AssemblyLanguageSourceCode
from pe_parser.x86_types import x86Type
import array
import nltk


class AssemblyParser:
    def __init__(self, asm_filepath: str):
        """
       Constructor method

       Parameters
       ----------
        asm_filepath: str
            Filepath of the assembly language source code file
       """
        if not os.path.isfile(asm_filepath):
            raise IOError
        self.asm_filepath = asm_filepath

        # processed values
        self.metadata_features = None
        self.symbol_features = None
        self.register_features = None
        self.api_features = None
        self.misc_features = None
        self.section_features = None
        self.data_define_features = None
        self.opcode_features = None

    def extract_assembly_language_source_code(self, asm_filepath=None):
        """
        Extracts a compressed representation of the assembly language source code.

        Parameters
        ----------
            asm_filepath: str
                Filepath of the assembly language source code file of an executable

        Return
        ----------
            source_code: AssemblyLanguageSourceCode
                Intermediate representation of the assembly language source code of an executable

        """
        if asm_filepath == None:
            parser = AssemblyLanguageInstructionsParser(self.asm_filepath)
        else:
            parser = AssemblyLanguageInstructionsParser(asm_filepath)
        parser.load_vocabulary()
        self.mnemonics_vocabulary = parser.mnemonics_vocabulary
        self.size_directives_vocabulary = parser.size_directives_vocabulary
        self.registers_vocabulary = list(parser.registers_vocabulary) #It is converted to a list for indexing purposes
        self.jcc_instructions = parser.jcc_vocabulary
        assembly_language_statements = parser.extract_assembly_language_statements()
        assembly_language_statements = self.clean_assembly_language_statements(assembly_language_statements)
        self.var_table = parser.variable_table
        self.source_code = AssemblyLanguageSourceCode(x86_instructions=assembly_language_statements)
        return self.source_code

    def clean_assembly_language_statements(self, assembly_language_statements: list):
        """
        Remove/clean unwanted assembly language statements

        Parameters
        ----------
            assembly_language_statements: list
                List of assembly language statements
        Return
        ----------
            reduced_assembly_language_statements: list
                Filtered list of assembly language statements
        """
        reduced_assembly_language_statements = []
        last_instruction = None
        for i in range(len(assembly_language_statements)):
            if assembly_language_statements[i].type != x86Type.NOT_A_STATEMENT:
                if assembly_language_statements[i].instruction_statement[0] == 'stop_line' and \
                        assembly_language_statements[i].instruction_statement[0] == last_instruction:
                    continue
                else:
                    reduced_assembly_language_statements.append(assembly_language_statements[i])
                    last_instruction = assembly_language_statements[i].instruction_statement[0]
            else:
                reduced_assembly_language_statements.append(assembly_language_statements[i])
                last_instruction = assembly_language_statements[i].instruction_statement
        return reduced_assembly_language_statements

    def get_opcodes_data_as_list(self, vocabulary_mapping: None):
        """
        Extracts the list of opcodes from the assembly language instructions of a PE file.

        Parameters
        ----------
            vocabulary_mapping: dict
                Mapping between opcodes and ID
        Return
        ---------
            opcodes: list
                List of opcodes
        """
        opcodes = []
        for x86_instruction in self.source_code.x86_instructions:
            if x86_instruction.type != x86Type.NOT_A_STATEMENT:
                if x86_instruction.instruction_statement[0] in vocabulary_mapping.keys():
                    opcodes.append(x86_instruction.instruction_statement[0])
                elif "loc_" in x86_instruction.instruction_statement[0]:
                    opcodes.append("loc_")
                elif "sub_" in x86_instruction.instruction_statement[0]:
                    opcodes.append("sub_")
                else:
                    opcodes.append("UNK")
            else:
                opcodes.append("NONE")
        return opcodes

    def get_opcodes(self):
        opcodes = []
        for x86_instruction in self.source_code.x86_instructions:
            if x86_instruction.type != x86Type.NOT_A_STATEMENT:
                if x86_instruction.instruction_statement[0] in self.mnemonics_vocabulary:
                    opcodes.append(x86_instruction.instruction_statement[0])
        return opcodes


    def extract_asm_metadata_features(self):
        """
        Extracts metadata features, i.e. the size of the file, and the number of lines in the file.

        Return
        ---------
            metadata_features: collections.OrderedDict()
                Dictionary of features
        """
        metadata_features = collections.OrderedDict()
        statinfo = os.stat(self.asm_filepath)
        file_size = statinfo.st_size
        metadata_features["ASM_MD_FileSize"] = file_size

        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            lines = asm_file.readlines()
            number_of_lines = len(lines)
        metadata_features["ASM_MD_NumLines"] = number_of_lines
        self.metadata_features = metadata_features
        return metadata_features

    def extract_symbol_features(self):
        """
        Extract the frequencies of the following set of symbols (SYM) -,+,*,],[,?,@

        Return
        ---------
            symbol_features: collections.OrderedDict()
                Dictionary of features
        """
        symbol_features = collections.OrderedDict()
        symbols = [0] * 7
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                if '*' in row:
                    symbols[0] += 1
                if '-' in row:
                    symbols[1] += 1
                if '+' in row:
                    symbols[2] += 1
                if '[' in row:
                    symbols[3] += 1
                if ']' in row:
                    symbols[4] += 1
                if '@' in row:
                    symbols[5] += 1
                if '?' in row:
                    symbols[6] += 1
        symbol_features["ASM_SYMBOLS_*"] = symbols[0]
        symbol_features["ASM_SYMBOLS_-"] = symbols[1]
        symbol_features["ASM_SYMBOLS_+"] = symbols[2]
        symbol_features["ASM_SYMBOLS_left_bracket"] = symbols[3]
        symbol_features["ASM_SYMBOLS_right_bracket"] = symbols[4]
        symbol_features["ASM_SYMBOLS_@"] = symbols[5]
        symbol_features["ASM_SYMBOLS_?"] = symbols[6]
        self.symbol_features = symbol_features
        return symbol_features

    def extract_opcode_unigram_features(self, opcodes=None):
        """
        Extract the frequences of a subset of 93 operation codes  based either on their commonness, or on their frequent
        use in malicious applications,

        Parameters
        ----------
            opcodes: list
                List of opcodes

        Return
        ---------
            opcode_features: collections.OrderedDict()
                Dictionary of features
        """
        if opcodes is None:
            opcodes = []
            with open(os.path.dirname(os.path.abspath(__file__))+"/vocabulary/small_subset_opcodes.txt") as opcodes_file:
                lines = opcodes_file.readlines()
                for line in lines:
                    opcode = line.strip()
                    opcodes.append(opcode)
            """
            opcodes = ['add','al','bt','call','cdq','cld','cli','cmc','cmp','const','cwd','daa','db'
                    ,'dd','dec','dw','endp','ends','faddp','fchs','fdiv','fdivp','fdivr','fild'
                    ,'fistp','fld','fstcw','fstcwimul','fstp','fword','fxch','imul','in','inc'
                    ,'ins','int','jb','je','jg','jge','jl','jmp','jnb','jno','jnz','jo','jz'
                    ,'lea','loope','mov','movzx','mul','near','neg','not','or','out','outs'
                    ,'pop','popf','proc','push','pushf','rcl','rcr','rdtsc','rep','ret','retn'
                    ,'rol','ror','sal','sar','sbb','scas','setb','setle','setnle','setnz'
                    ,'setz','shl','shld','shr','sidt','stc','std','sti','stos','sub','test'
                    ,'wait','xchg','xor']
            """
        opcode_features = collections.OrderedDict({"ASM_1GRAM_OPCODES_{}".format(opcode): 0 for opcode in opcodes})
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                parts = row.split()

                for opcode in opcodes:
                    if opcode in parts:
                        opcode_features["ASM_1GRAM_OPCODES_{}".format(opcode)] += 1
                        break
        self.opcode_features = opcode_features
        return opcode_features

    def extract_register_features(self, registers=None):
        """
        Extract the frequency of use of the registers in the assembly language source code of malware

        Parameters
        ----------
            registers: list
                List of registers

        Return
        ---------
            opcode_features: collections.OrderedDict()
                Dictionary of features
        """
        if registers is None:
            registers = []
            with open(os.path.dirname(os.path.abspath(__file__))+"/vocabulary/registers.txt") as registers_file:
                lines = registers_file.readlines()
                for line in lines[1:]:
                    register = line.strip()
                    registers.append(register)
        register_features = collections.OrderedDict({"ASM_REG_{}".format(register): 0 for register in registers})
        #print(register_features.keys())
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                parts = row.split()
                for register in registers:
                    if register in parts:
                        register_features["ASM_REG_{}".format(register)] += 1
                        break
        #print(register_features)
        self.register_features = register_features
        return register_features

    def extract_API_features(self, APIs=None):
        """
        Extract the frequencies of a subset of 794 frequent APIs

        Parameters
        ----------
            APIs: list
                List of API functions

        Return
        ---------
            api_features: collections.OrderedDict()
                Dictionary of features
        """
        if APIs is None:
            apis = []
            with open(os.path.dirname(os.path.abspath(__file__))+"/vocabulary/subset_APIs.txt") as apis_file:
                lines = apis_file.readlines()
                for line in lines:
                    api = line.strip()
                    apis.append(api)
        api_features = collections.OrderedDict({"ASM_API_{}".format(api): 0 for api in apis})
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                for i in range(len(apis)):
                    if apis[i] in row:
                        api_features["ASM_API_{}".format(apis[i])] += 1
                        break
        self.api_features = api_features
        return api_features

    def extract_MISC_features(self, keywords=None):
        """
        Extract the frequencies of a 95 manually chosen keywords (MISC) from the disassembled code

        Parameters
        ----------
            keywords: list
                List of keywords

        Return
        ---------
            misc_features: collections.OrderedDict()
                Dictionary of features
        """
        if keywords is None:
            keywords = []
            with open(os.path.dirname(os.path.abspath(__file__))+"/vocabulary/misc_keywords.txt") as keywords_file:
                lines = keywords_file.readlines()
                for line in lines:
                    keyword = line.strip()
                    keywords.append(keyword)
        misc_features = collections.OrderedDict({"ASM_MISC_{}".format(keyword): 0 for keyword in keywords})
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                for i in range(len(keywords)):
                    if keywords[i] in row:
                        misc_features["ASM_MISC_{}".format(keywords[i])] += 1
                        break
        self.misc_features = misc_features
        return misc_features

    def extract_section_features(self):
        """
        Extract features from the PE sections

        Return
        ---------
            section_features: collections.OrderedDict()
                Dictionary of features
        """
        section_names = []
        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            lines = asm_file.readlines()
            for row in lines:
                try:
                    section_name = [row[0:np.core.defchararray.index(row, ':')]]
                    if section_name != 'HEADER':
                        section_names += section_name
                except ValueError as ve:
                    continue

        known_sections = ['.text', '.data', '.bss', '.rdata', '.edata', '.idata', '.rsrc', '.tls', '.reloc']
        sections_values = [0] * 24
        unknown_sections = []
        unknown_lines = 0
        number_of_sections = len(section_names)
        for section in section_names:

            if section in known_sections:
                section_index = known_sections.index(section)
                sections_values[section_index] += 1
            else:
                unknown_sections.append(section)
                unknown_lines += 1

        uni_section_names_len = len(np.unique(section_names))
        uni_unknown_section_names_len = len(np.unique(unknown_sections))
        uni_known_section_names_len = 0
        for i in range(0, 8):
            if sections_values[i] != 0:
                uni_known_section_names_len += 1

        sections_values[9] = uni_section_names_len
        sections_values[10] = uni_unknown_section_names_len
        sections_values[11] = unknown_lines

        for i in range(0, 8):
            sections_values[i + 12] = float(sections_values[i]) / number_of_sections

        sections_values[21] = float(uni_known_section_names_len) / uni_section_names_len
        sections_values[22] = float(uni_unknown_section_names_len) / uni_section_names_len
        sections_values[23] = float(unknown_lines) / number_of_sections

        feature_names = header_asm_sections()
        self.section_features = collections.OrderedDict(
                {"ASM_SECTION_{}".format(feature_names[i]): sections_values[i] for i in range(len(feature_names))})

        return self.section_features

    def extract_data_define_features(self):
        """
        Extract features related to data defines dd, dw, etc.

        Return
        ---------
            data_define_features: collections.OrderedDict()
                Dictionary of features
        """
        dbCounter = 0
        ddCounter = 0
        dwCounter = 0
        dcCounter = 0
        db0Counter = 0
        dbN0Counter = 0

        all = 0
        text = 0
        rdata = 0
        data = 0
        dd_text = 0
        db_text = 0
        dd_rdata = 0
        db3_rdata = 0
        db3_data = 0
        db3_all = 0
        dd4 = 0
        dd5 = 0
        dd6 = 0

        all = 0

        text = 0
        rdata = 0
        data = 0
        idata = 0
        # NotdataNottext
        NdNt = 0

        db3_idata = 0
        db3_text = 0
        db3_rsrc = 0
        db3_NdNt = 0
        db3_all = 0
        db3_zero = 0

        dd_text = 0
        db_text = 0
        dd_rdata = 0
        db3_data = 0
        db3_all = 0
        dd4_NdNt = 0
        dd5_NdNt = 0
        dd6_NdNt = 0

        with open(self.asm_filepath, "r", encoding="ISO-8859-1") as asm_file:
            asm_code = asm_file.readlines()
            for row in asm_code:
                RowItems = row.split()
                Section = row.split(':')[0]
                RowComma = row.split(',')

                all += 1
                dbCounter += RowItems.count('db')
                ddCounter += RowItems.count('dd')
                dwCounter += RowItems.count('dw')
                if len(RowItems) > 3:
                    if RowItems[1] == '00' and RowItems[2] == 'db':
                        db0Counter += 1

                if Section == '.text':
                    text += 1
                    dd_text += RowItems.count('dd')
                    db_text += RowItems.count('db')
                elif Section == '.rdata':
                    rdata += 1
                    dd_rdata += RowItems.count('dd')
                    if len(RowItems) == 4 or len(RowItems) == 6:
                        if RowItems[2] == 'db':
                            db3_rdata += RowItems.count('db')
                elif Section == '.data':
                    data += 1
                    if len(RowItems) == 4 or len(RowItems) == 6:
                        if RowItems[2] == 'db':
                            db3_data += RowItems.count('db')

                if len(RowItems) == 4 or len(RowItems) == 6:
                    if RowItems[2] == 'db':
                        db3_all += RowItems.count('db')
                elif Section == '.idata':
                    idata += 1
                    if len(RowItems) == 4 or len(RowItems) == 6:
                        if RowItems[2] == 'db':
                            db3_idata += 1
                else:
                    NdNt += 1
                    if len(RowItems) == 4 or len(RowItems) == 6:
                        if RowItems[2] == 'db':
                            db3_NdNt += 1

                    if len(RowComma) == 4:
                        dd4_NdNt += RowItems.count('dd')

                    if len(RowComma) == 5:
                        dd5_NdNt += RowItems.count('dd')

                    if len(RowComma) == 6:
                        dd6_NdNt += RowItems.count('dd')

                if len(RowComma) == 4:
                    dd4 += RowItems.count('dd')

                if len(RowComma) == 5:
                    dd5 += RowItems.count('dd')

                if len(RowComma) == 6:
                    dd6 += RowItems.count('dd')

                if len(RowItems) == 4 or len(RowItems) == 6:
                    if RowItems[2] == 'db':
                        db3_all += 1
                        if RowItems[1] == '00':
                            db3_zero += 1

            dcCounter = dbCounter + ddCounter + dwCounter
            db_por = float(dbCounter) / all
            dd_por = float(ddCounter) / all
            dw_por = float(dwCounter) / all
            dc_por = float(dcCounter) / all
            db0_por = dbN0_por = 0
            if dbCounter != 0:
                db0_por = float(db0Counter) / dbCounter
                dbN0_por = float(dbCounter - db0Counter) / dbCounter

            ############################

            Res_dd_text = 0
            Res_db_text = 0
            Res_dd_rdata = 0
            Res_db3_rdata = 0
            Res_db3_data = 0

            if text != 0:
                Res_dd_text = float(dd_text) / text
                Res_db_text = float(db_text) / text

            if rdata != 0:
                Res_dd_rdata = float(dd_rdata) / rdata
                Res_db3_rdata = float(db3_rdata) / rdata

            if data != 0:
                Res_db3_data = float(db3_data) / data

            Res_db3_all = float(db3_all) / all

            Res_dd4_all = float(dd4) / all
            Res_dd5_all = float(dd5) / all
            Res_dd6_all = float(dd6) / all

            Output = [Res_dd_text, Res_db_text, Res_dd_rdata, Res_db3_rdata, Res_db3_data, Res_db3_all, dd4, dd5, dd6,
                      Res_dd4_all, Res_dd5_all, Res_dd6_all]

            Res_db3_idata = 0
            Res_db3_NdNt = 0
            Res_dd4_NdNt = 0
            Res_dd5_NdNt = 0
            Res_dd6_NdNt = 0
            Res_db3_all_zero = 0

            if idata != 0:
                Res_db3_idata = float(db3_idata) / idata

            if NdNt != 0:
                Res_db3_NdNt = float(db3_NdNt) / NdNt
                Res_dd4_NdNt = float(dd4_NdNt) / NdNt
                Res_dd5_NdNt = float(dd5_NdNt) / NdNt
                Res_dd6_NdNt = float(dd6_NdNt) / NdNt

            if db3_all != 0:
                Res_db3_all_zero = float(db3_zero) / db3_all

            Output2 = [Res_db3_idata, Res_db3_NdNt, Res_dd4_NdNt, Res_dd5_NdNt, Res_dd6_NdNt, Res_db3_all_zero]

            feature_values = [db_por, dd_por, dw_por, dc_por, db0_por, dbN0_por] + Output + Output2

            feature_names = header_asm_data_define()

            self.data_define_features = collections.OrderedDict(
                {"ASM_DD_{}".format(feature_names[i]): feature_values[i] for i in range(len(feature_names))})
            return self.data_define_features
            # helper methods

    def convert_asm_to_img(self):
        """
        Converts the assembly language source code into a grayscale image.

        Return
        ---------
            asm_img: np.array
                Grayscale image representation of malware's assembly language source code
        """
        import codecs
        f = codecs.open(self.asm_filepath, "rb")
        ln = os.path.getsize(self.asm_filepath)
        width = int(ln**0.5)
        rem = int(ln/width)
        a = array.array("B")
        a.frombytes(f.read())
        f.close()
        g = np.reshape(a[:width*width], (width, width))
        self.asm_img = np.uint(g)
        return self.asm_img

    def extract_pixel_intensities(self, num_pixels=800, asm_img=None):
        """
        Extracts the first 'num_pixels' pixels of the grayscale image representation of malware as features

        Parameters
        ----------
            num_pixels: int
                Number of pixels
            asm_img: np.array
                Grayscale image representation of the executable
        Return
        ---------
            pixel_intensity_features: collections.OrderedDict
                Dictionary of features
        """
        self.pixel_intensity_features = collections.OrderedDict()
        if asm_img is None:
            asm_img = self.asm_img
        flattened_img = asm_img.flatten()
        for i in range(num_pixels):
            self.pixel_intensity_features["ASM_PIXEL_{}th".format(i)] = flattened_img[i]
        return self.pixel_intensity_features

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
        opcodes = self.get_opcodes()
        fdist = self.extract_ngrams_freq(opcodes, N)
        return fdist












