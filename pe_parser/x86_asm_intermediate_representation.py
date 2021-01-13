from pe_parser.x86_types import x86Type
from pe_parser.x86_instr import x86Instr
import json


class AssemblyLanguageSourceCode(object):
    def __init__(self, x86_instructions=None, ID=None, CLASS=None):
        self.ID = ID
        self.CLASS = CLASS
        if x86_instructions is not None:
            self.x86_instructions = x86_instructions
        else:
            self.x86_instructions = []

    def get_dead_code_locations(self):
        dead_code_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.NORMAL]
        return dead_code_locations

    def get_jcc_locations(self):
        jcc_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.JMP_JCC]
        return jcc_locations

    def get_mem_locations(self):
        mem_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.MEM]
        return mem_locations

    def get_start_locations(self):
        start_locations = [i for i, x86instr in enumerate(self.x86_instructions) if x86instr.type == x86Type.LOCATION]
        return start_locations


    def load(self, filepath):
        with open(filepath, "r") as input_file:
            data = json.load(input_file)
            self.deserialize(data)


    def serialize(self):
        self.serialized_data = {"Id": self.ID,
                "Class": self.CLASS,
                "SourceCode": [x86_instruction.serialize() for x86_instruction in self.x86_instructions]}
        return self.serialized_data

    def deserialize(self, data):
        self.ID = data['Id']
        self.CLASS = data['Class']
        self.x86_instructions = []
        for sample in data['SourceCode']:
            x86_instruction = x86Instr(sample['address'],
                                       sample['bytes'],
                                       sample['instruction'],
                                       sample['type'])
            self.x86_instructions.append(x86_instruction)

    def save(self, filepath):
        with open(filepath, "w") as output_file:
            json.dump(self.serialize(), output_file)

    def write_source_to_file(self):
        print("print(): ToImplement")