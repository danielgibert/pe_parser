import copy

class x86Instr(object):
    def __init__(self, address, hex_sequence=None, instruction_statement=None, type=None):
        self.address = address
        self.hex_sequence = hex_sequence
        self.instruction_statement = instruction_statement
        self.type = type

    def __str__(self):
        if self.hex_sequence is not None:
            if self.instruction_statement is None:
                return str(self.address) + ";" + " ".join(self.hex_sequence) + ";" + " " + "; Type: {}".format(self.type)
            else:
                #print(self.address, self.hex_sequence, self.instruction_statement)
                return str(self.address) + ";" + " ".join(self.hex_sequence) + ";" + " ".join(self.instruction_statement) + "; Type: {}".format(self.type)
        else:
            if self.instruction_statement is None:
                return str(self.address) + ";" + " " + "; Type: {}".format(self.type)
            else:
                #print(self.address, self.instruction_statement)
                return str(self.address) + ";" + " ".join(self.instruction_statement) + "; Type: {}".format(self.type)

    def copy(self):
        return x86Instr(copy.copy(self.address),
                        copy.copy(self.hex_sequence),
                        copy.copy(self.instruction_statement),
                        copy.copy(self.type))

    def serialize(self):
        self.serialized_data = {"address": self.address,
                "bytes": self.hex_sequence,
                "instruction": self.instruction_statement,
                "type": self.type}
        return self.serialized_data

    def deserialize(self, serialized_data):
        self.address = serialized_data["address"]
        self.hex_sequence = serialized_data["bytes"]
        self.instruction_statement = serialized_data["instruction"]
        self.type = serialized_data["type"]

    #def toJSON(self):
    #    return {"address": self.address,
    #            "bytes": self.hex_sequence,
    #            "instruction": self.instruction_statement,
    #            "type": self.type}