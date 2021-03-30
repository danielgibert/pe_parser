
class x86Type:
    """"
    Types of assembly language statements
    """
    NORMAL = 0
    DATA_DEFINE = 1
    JMP_JCC = 2
    SUBPROCESS = 3
    END_SUBPROCESS = 4
    LOCATION = 5
    STOP_LINE = 6
    MEM = 7
    NOT_A_STATEMENT = 8