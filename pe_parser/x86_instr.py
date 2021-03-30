import copy

class x86Instr(object):
    """
    Assembly language instruction
    """
    def __init__(self, address, hex_sequence=None, instruction_statement=None, type=None):
        """
        Class constructor

        Parameters
        ----------
            address: str
                Memory address associated to the instruction
            hex_sequence: list
                List of hexadecimal values associated to the instruction
            instruction_statement: list
                Assembly language instruction statement, i.e. ['add', 'eax', '1h']
            type: x86_types.x86Type
                Type of assembly language statement
        """
        self.address = address
        self.hex_sequence = hex_sequence
        self.instruction_statement = instruction_statement
        self.type = type

    def __str__(self):
        """
        Converts the x86Instr object to a string

        Return:
            string: str
                String representation of the object
        """
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
        """
        Performs a copy of the object

        Return
        ---------
            x86Instr: x86Instr
                Assembly language instruction object
        """
        return x86Instr(copy.copy(self.address),
                        copy.copy(self.hex_sequence),
                        copy.copy(self.instruction_statement),
                        copy.copy(self.type))

    def serialize(self):
        """
        Serializes the x86Instr object

        Return
        ---------
            serialized_data: dict
                Serialized object
        """
        self.serialized_data = {"address": self.address,
                "bytes": self.hex_sequence,
                "instruction": self.instruction_statement,
                "type": self.type}
        return self.serialized_data

    def deserialize(self, serialized_data: dict):
        """
        Deserializes the x86Instr object

        Parameters
        ---------
            serialized_data: dict
                Serialized object
        """
        self.address = serialized_data["address"]
        self.hex_sequence = serialized_data["bytes"]
        self.instruction_statement = serialized_data["instruction"]
        self.type = serialized_data["type"]

    #def toJSON(self):
    #    return {"address": self.address,
    #            "bytes": self.hex_sequence,
    #            "instruction": self.instruction_statement,
    #            "type": self.type}