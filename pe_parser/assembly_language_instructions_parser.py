import argparse
import os
import csv
import sys
from pe_parser.x86_instr import x86Instr
from pe_parser.x86_types import x86Type
from pe_parser.utils import read_tokens_from_csv

class AssemblyLanguageInstructionsParser(object):
    """
    Assembly Language Parser object
    """
    def __init__(self, filepath: str):
        """
        Class constructor

        Parameters
        ----------
            filepath: str
                Filepath of the assembly language source code file
        """
        if not os.path.isfile(filepath):
            raise IOError
        self.pe_filepath = filepath
        self.variable_table = dict()

    def load_vocabulary(self,
                        opcodes_vocabulary_filepath=None,
                        registers_vocabulary_filepath=None,
                        data_define_vocabulary_filepath=None,
                        jcc_vocabulary_filepath=None):
        """
        Loads the predefined vocabulary to memory. By default, various vocabulary files are provided but this might be
        modified by the final user depending on their objectives

        Parameters
        ----------
            opcodes_vocabulary_filepath: str
                Filepath of the file containing the opcodes vocabulary
            registers_vocabulary_filepath: str
                Filepath of the file containing the registers vocabulary
            data_define_vocabulary_filepath: str
                Filepath of the file containing the data define directives vocabulary
            jcc_vocabulary_filepath: str
                Filepath of the file containing the jump instructions vocabulary
         """
        # x86 opcodes
        if opcodes_vocabulary_filepath is not None and os.path.isfile(opcodes_vocabulary_filepath):
            with open(opcodes_vocabulary_filepath) as opcodes_file:
                opcodes_list = [row['mnemonic'] for row in csv.DictReader(opcodes_file)]
                self.opcodes_list = sorted(opcodes_list)[1:]  # Removes key:''
            self.mnemonics_vocabulary = read_tokens_from_csv(opcodes_vocabulary_filepath, "mnemonic")
        else:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   "vocabulary/full_mnemonics.txt")) as opcodes_file:
                opcodes_list = [row['mnemonic'] for row in csv.DictReader(opcodes_file)]
                self.opcodes_list = sorted(opcodes_list)[1:]  # Removes key:''
            self.mnemonics_vocabulary = read_tokens_from_csv(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/full_mnemonics.txt"), "mnemonic")

        # Data define directives
        if data_define_vocabulary_filepath is not None and os.path.isfile((data_define_vocabulary_filepath)):
            with open(data_define_vocabulary_filepath) as data_define_file:
                self.data_define_list = [row['data_define'] for row in csv.DictReader(data_define_file)]
            self.data_define_vocabulary = read_tokens_from_csv(data_define_vocabulary_filepath, "data_define")

        else:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/data_defines.txt")) as data_define_file:
                self.data_define_list = [row['data_define'] for row in csv.DictReader(data_define_file)]
            self.data_define_vocabulary = read_tokens_from_csv(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/data_defines.txt"), "data_define")
        self.size_directives_vocabulary = read_tokens_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/size_directives.txt"), "directive")

        # Registers vocabulary
        if registers_vocabulary_filepath is not None and os.path.isfile(registers_vocabulary_filepath):
            with open(registers_vocabulary_filepath) as registers_file:
                self.registers_list = [row['register'] for row in csv.DictReader(registers_file)]
            self.registers_vocabulary = read_tokens_from_csv(registers_vocabulary_filepath, "register")
        else:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   "vocabulary/x86_registers.txt")) as registers_file:
                self.registers_list = [row['register'] for row in csv.DictReader(registers_file)]
            self.registers_vocabulary = read_tokens_from_csv(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/x86_registers.txt"), "register")
        # Jcc vocabulary
        if jcc_vocabulary_filepath is not None and os.path.isfile((jcc_vocabulary_filepath)):
            with open(jcc_vocabulary_filepath) as jcc_file:
                self.jcc_list = [row['jcc'] for row in csv.DictWriter(jcc_file)]
            self.jcc_vocabulary = read_tokens_from_csv(jcc_vocabulary_filepath, "jcc")
        else:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   "vocabulary/jcc_instructions.txt")) as jcc_file:
                self.jcc_list = [row['jcc'] for row in csv.DictReader(jcc_file)]
            self.jcc_vocabulary = read_tokens_from_csv(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "vocabulary/jcc_instructions.txt"), "jcc")

    def print_nonprocessed_statements(self):
        """
        This piece of code is used to get those lines that are not being processed from the asm file.  Data not useful.
        In consequence, the data is lost forever...
        This function is mostly used for debugging purposes
        """
        try:
            with open(self.pe_filepath, "r", encoding="ISO-8859-1") as input_file:
                statements = []
                lines = input_file.readlines()
                non_processed_lines = []
                print("{}; Length: {}".format(self.pe_filepath, len(lines)))
                i = 1
                for line in lines:
                    try:
                        x86_statement = self.extract_statement(line)
                        if x86_statement is not None:
                            statements.append(x86_statement)
                        else:
                            non_processed_lines.append((i, line))
                    except TypeError as e:
                        continue
                    i += 1
                print("Statements: {}".format(len(statements)))
        except TypeError as e:
            with open(self.pe_filepath, "r") as input_file:
                statements = []
                lines = input_file.readlines()
                print("{}; Length: {}".format(self.pe_filepath, len(lines)))
                i = 1
                for line in lines:
                    try:
                        x86_statement = self.extract_statement(line)
                        if x86_statement is not None:
                            statements.append(x86_statement)
                        else:
                            non_processed_lines.append((i, line))
                    except TypeError as e:
                        continue
                i +=1
            print("Statements: {}".format(len(statements)))

        asm_filename = self.pe_filepath.split("/")[-1]
        with open("logs/{}.log".format(asm_filename), "w") as output_file:
            for line in non_processed_lines:
                output_file.write("{};{}".format(line[0], line[1]))

    def extract_assembly_language_statements(self):
        """
        Preprocesses the assembly language source code and retrieves its assembly language statements

        Return
        ---------
            statements: list
                List of assembly language statements
        """
        try:
            with open(self.pe_filepath, "r", encoding = "ISO-8859-1") as input_file:
                statements = []
                lines = input_file.readlines()
                #print("{}; Length: {}".format(self.pe_filepath, len(lines)))
                for line in lines:
                    try:
                        x86_statement = self.extract_statement(line)
                        if x86_statement is not None:
                            statements.append(x86_statement)
                    except TypeError as e:
                        continue
                #print("Statements: {}".format(len(statements)))
            return statements
        except TypeError as e:
            with open(self.pe_filepath, "r") as input_file:
                statements = []
                lines = input_file.readlines()
                #print("{}; Length: {}".format(self.pe_filepath, len(lines)))
                for line in lines:
                    try:
                        x86_statement = self.extract_statement(line)
                        if x86_statement is not None:
                            statements.append(x86_statement)
                    except TypeError as e:
                        continue
            #print("Statements: {}".format(len(statements)))
            return statements

    def extract_statement(self, line: str):
        """
        Extracts the information of a particular assembly language statement

        Return
        ---------
            statement: x86Instr
                Assembly language instruction
        """
        mem_tokens = ["unk_",
                      "sub_",
                      "loc_",
                      "off_",
                      "dword_",
                      "byte_"]
        try:
            line = line.strip()
            tokens = line.split() # Split line with '\ ', '\t', etc
            # Remove comments
            tokens = " ".join(tokens)
            tokens = tokens.split(";")

            if 1 <= len(tokens) <= 3:
                tokens = tokens[0].split(" ")
            else:
                return None
            """
            if len(tokens) == 1:
                tokens = tokens[0].split(" ")
            elif len(tokens) == 2:
                #There is a comment
                tokens = tokens[0].split(" ")
            elif len(tokens) == 3:
                print(tokens)

                tokens = tokens[0].split(" ")
            """

            for i in range(len(tokens)):
                #print(tokens)
                """
                try:
                    mnemonics_vocabulary[tokens[i]]
                    try: # Checks if it is the IN instruction or the "in" inside  "Section size in file" string
                        if tokens[i+1] == "file":
                            return None
                    except IndexError:
                        continue
                    hex_representation = tokens[1:i]
                    if len(hex_representation) > 0:
                        #print(hex_representation, tokens)
                        if hex_representation[0] != ";":
                            address = tokens[0].split(":")[1]
                            if tokens[i+1] is not None:
                                assembly_language_statement = self.get_clean_asm_statement(tokens[i:])
                                if assembly_language_statement is not None:
                                    return x86_inst(address, hex_representation, assembly_language_statement)
                except ValueError as e:
                    continue
                """
                if tokens[i] in self.mnemonics_vocabulary:

                    try: # Checks if it is the IN instruction or the "in" inside  "Section size in file" string
                        if tokens[i+1] == "file":
                            print("WTF")
                            return None
                    except IndexError as ie:
                        #print(ie)
                        continue
                    if tokens[i] in self.jcc_vocabulary:
                        statement_type = x86Type.JMP_JCC
                    else:
                        statement_type = x86Type.NORMAL

                    # Let's extract the hexadecimal representation
                    hex_representation = tokens[1:i]
                    if len(hex_representation) > 0:
                        #print(hex_representation, tokens)
                        if hex_representation[0] != ";":
                            address = tokens[0].split(":")[1]
                            # Now it's time to extract the assembly language statement
                            #if tokens[i+1] is not None: # For what reaseon there is this None here, I have no fucking clue
                            unclean_statement = [x.replace(",","") for x in tokens[i:]]
                            assembly_language_statement = self.get_clean_asm_statement(unclean_statement)
                            #assembly_language_statement = self.get_clean_asm_statement(tokens[i:])
                            if assembly_language_statement is not None:
                                clean_asm_statement = []
                                for token in assembly_language_statement:
                                    if token != '':
                                        clean_asm_statement.append(token)
                                    if statement_type is not x86Type.JMP_JCC:
                                        for mem_token in mem_tokens:
                                            if mem_token in token:
                                                statement_type = x86Type.MEM
                                #assembly_language_statement = [token for token in assembly_language_statement if token != '']
                                return x86Instr(address, hex_representation, clean_asm_statement, statement_type)
                elif "loc_" in tokens[i]:
                    address = tokens[0].split(":")[-1]
                    if ":" in tokens[i]:
                        return x86Instr(address, None, [tokens[i][:-1]], x86Type.LOCATION)
                    return x86Instr(address, None, [tokens[i]], x86Type.LOCATION)
                elif "sub_" in tokens[i]:
                    address = tokens[0].split(":")[-1]
                    try:
                        if "endp" in tokens[i + 1]:
                            return x86Instr(address, None, ["endp"], x86Type.END_SUBPROCESS)
                        else:
                            return x86Instr(address, None, [tokens[i]], x86Type.SUBPROCESS)
                    except IndexError:
                        return x86Instr(address, None, [tokens[i]], x86Type.SUBPROCESS)
                # Data defines
                elif tokens[i] in self.data_define_vocabulary:
                    address = tokens[0].split(":")[-1]
                    hex_representation = tokens[1:i]
                    if address == ".r":
                        # The bug is occurring. Following there is an example:
                        # tokens = ['.r', '.rdata:0073116B', '0A', 'db', '0Ah']
                        # tokens[0] == '.r'
                        # Start calculations in tokens[1]
                        address = tokens[1].split(":")[-1]
                        hex_representation = tokens[2:i]
                        return x86Instr(address, hex_representation, [tokens[i]], x86Type.DATA_DEFINE)

                    return x86Instr(address, hex_representation, [tokens[i]], x86Type.DATA_DEFINE)
                elif "var_" in tokens[i] or "arg_" in tokens[i]:
                    # Add to variable's table lookup
                    next_element = 2
                    if tokens[i] not in self.variable_table.keys() and len(tokens[i:]) > 1:
                        self.variable_table[tokens[i]] = tokens[i+next_element:]

            if ";" in line and "---" in line:
                address = tokens[0].split(":")[-1]
                return x86Instr(address, None, ["stop_line"], x86Type.STOP_LINE)
            elif ";" in line and "===" in line:
                address = tokens[0].split(":")[-1]
                return x86Instr(address, None, ["stop_line"], x86Type.STOP_LINE)

            else:
                # What to do in any other situation. Just get the bytes and get the hell out...
                try:
                    address = tokens[0].split(":")[1]
                    hex_sequence = []
                    for hex_str in tokens[1:]:
                        try:
                            if "+" == hex_str[-1]:
                                hex_str = hex_str[:-1]
                        except IndexError as ie1:
                            continue
                        if len(hex_str) == 2:
                            try:
                                int_value = int(hex_str, 16)
                                if 0 <= int_value <= 255:
                                    hex_sequence.append(hex_str)
                            except ValueError:
                                if hex_str == "??":
                                    hex_sequence.append(hex_str)
                                continue
                    if len(hex_sequence) > 0:
                        return x86Instr(address, hex_sequence, None, x86Type.NOT_A_STATEMENT)
                    else:
                        return None
                except IndexError as ie2:
                    print(ie2)
                    print(tokens)
                    return None
        except UnicodeDecodeError as e:
            print("Exception {}".format(e))
            return None
        return None

    def get_clean_asm_statement(self, asm_statement):
        """
        Remove unwanted assembly language statements.

        Parameter
        ---------
            asm_statement: x86Instr
                Assembly language statement

        Return
        ---------
            asm_statement: x86Instr
                Assembly language statement
        """

        # Remove weird statements
        if asm_statement[0] != ';':
            # Remove comments
            for i in range(len(asm_statement)):
                if asm_statement[i] == ';':
                    asm_statement = asm_statement[:i]
                    break
            if asm_statement[0] == 'int':
                if len(asm_statement) == 2:
                    try:
                        int(asm_statement[1], 16)
                        return asm_statement
                    except ValueError as e:
                        if len(asm_statement[1])==3 and asm_statement[1][-1] == "h":
                            try:
                                int(asm_statement[1][:-1], 16)
                                return asm_statement
                            except ValueError as e2:
                                return None
                elif len(asm_statement) == 3 and asm_statement[2] == "":
                    try:
                        int(asm_statement[1], 16)
                        return asm_statement[:-1]
                    except ValueError as e:
                        if len(asm_statement[1])==3 and asm_statement[1][-1] == "h":
                            try:
                                int(asm_statement[1][:-1], 16)
                                return asm_statement[:-1]
                            except ValueError as e2:
                                return None
                        return None
                else:
                    return None

            elif asm_statement[0] == 'not':
                if len(asm_statement) == 2 or len(asm_statement) == 4:
                    return asm_statement
            elif asm_statement[0] == 'or':
                if 3 <= len(asm_statement) <= 5:
                    return asm_statement
                #if (3 <= len(asm_statement) <= 4 or asm_statement[1] == "dword") and asm_statement[1] != "from":
                #if asm_statement[1] in self.registers_vocabulary or asm_statement[1] == "dword" or asm_statement[1] == "byte" or asm_statement[1] == "ptr":
                #    return asm_statement
            elif asm_statement[0] == "in":
                if len(asm_statement) == 3:
                    return asm_statement
                elif len(asm_statement) == 4:
                    if asm_statement[-1] == "":
                        return asm_statement[:-1]
            else:
                if asm_statement is not None:
                    return asm_statement
        return None
