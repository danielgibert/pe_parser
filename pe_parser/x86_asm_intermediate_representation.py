from pe_parser.x86_types import x86Type
from pe_parser.x86_instr import x86Instr
import json


class AssemblyLanguageSourceCode(object):
    """
    Intermediate representation of an assembly language source code file
    """
    def __init__(self, x86_instructions=None, ID=None, CLASS=None):
        """
        Class constructor

        Parameters
        ----------
        x86_instructions: list
            List of x86Instr
        Id: str
            ID of the assembly language source code file
        CLASS: int
            Family associated to the ID
        """
        self.ID = ID
        self.CLASS = CLASS
        if x86_instructions is not None:
            self.x86_instructions = x86_instructions
        else:
            self.x86_instructions = []

    def get_dead_code_locations(self):
        """
        Return a list containing the positions where it is possible to insert a dead code instruction

        Return
        ---------
            dead_code_locations: list
                List of positions
        """
        dead_code_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.NORMAL]
        return dead_code_locations

    def get_jcc_locations(self):
        """
        Return a list containing the positions of the jump, jcc instructions

        Return
        ---------
            jcc_locations: list
                List of positions
        """
        jcc_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.JMP_JCC]
        return jcc_locations

    def get_mem_locations(self):
        """
        Return a list containing the positions of memory addresses

        Return
        ---------
            mem_locations: list
                List of positions
        """
        mem_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.MEM]
        return mem_locations

    def get_start_locations(self):
        """
        Return a list containing the positions where the subroutines start

        Return
        ---------
            start_locations: list
                List of positions
        """
        start_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.LOCATION]
        return start_locations


    def load(self, filepath: str):
        """
        Loads an intermediate representation of an assembly language source code file into memory

        Parameters
        ----------
            filepath: str
                Filepath containing the intermediate representation of the asm file
        """
        with open(filepath, "r") as input_file:
            data = json.load(input_file)
            self.deserialize(data)


    def serialize(self):
        """
        Serializes the AssemblyLanguageSourceCode object

        Return
        ---------
            serialized_data: dict
                Dictionary containing the object's information
        """
        self.serialized_data = {"Id": self.ID,
                "Class": self.CLASS,
                "SourceCode": [x86_instruction.serialize() for x86_instruction in self.x86_instructions]}
        return self.serialized_data

    def deserialize(self, data: dict):
        """
        Deserializes the AssemblyLanguageSourceCode object

        Parameters
        ----------
            data: dict
                Dictionary containing the object's information
        """
        self.ID = data['Id']
        self.CLASS = data['Class']
        self.x86_instructions = []
        for sample in data['SourceCode']:
            x86_instruction = x86Instr(sample['address'],
                                       sample['bytes'],
                                       sample['instruction'],
                                       sample['type'])
            self.x86_instructions.append(x86_instruction)

    def save(self, filepath: str):
        """
        Dump the serialized AssemblyLanguageSourceCode object to a json file

        Parameters:
            filepath: str
                File where the object will be saved
        """
        with open(filepath, "w") as output_file:
            json.dump(self.serialize(), output_file)
