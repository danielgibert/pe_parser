import json
import csv

def header_asm_sections():
    """
    Return the feature names associated to the section features

    Return
    ---------
        colnames: list
            List of feature names
    """
    kown_sections = ['.text','.data','.bss', '.rdata','.edata','.idata', '.rsrc','.tls','.reloc']
    colnames = kown_sections + ['Num_Sections', 'Unknown_Sections', 'Unknown_Sections_lines']
    colnames += ['.text_por','.data_por','.bss_por', '.rdata_por','.edata_por',
                 '.idata_por', '.rsrc_por','.tls_por','.reloc_por']
    colnames += ['known_Sections_por', 'Unknown_Sections_por', 'Unknown_Sections_lines_por']
    return colnames

def header_asm_data_define():
    """
    Return the feature names associated to the data define features

    Return
    ---------
        colnames: list
            List of feature names
    """
    colnames = ['db_por','dd_por','dw_por','dc_por','db0_por','dbN0_por','dd_text',
                'db_text','dd_rdata','db3_rdata','db3_data','db3_all','dd4','dd5',
                'dd6','dd4_all','dd5_all','dd6_all']
    return colnames

def load_vocabulary(vocabulary_filepath):
    """
    It reads and stores in a dictionary-like structure the data from the file passed as argument

    Parameters
    ----------
        vocabulary_filepath: str
            JSON-like file

    Return
    ---------
        vocabulary_dict: dict
            Vocabulary mapping
    """
    with open(vocabulary_filepath, "r") as vocab_file:
        vocabulary_dict = json.load(vocab_file)
    return vocabulary_dict


def read_tokens_from_csv(csv_filepath, header):
    """
    Read tokens from a csv file

    Parameters
    ----------
        csv_filepath: str
            Filepath of the .csv file
        header: str
            header column name

    Return
    ---------
        tokens: set
            Set of tokens
    """
    with open(csv_filepath) as input_file:
        reader = csv.DictReader(input_file)
        return {row[header] for row in reader}

def save_fdist(fdist, output_filepath):
    fdist_dict = dict()
    for k,v in fdist.items():
        key = ",".join([token for token in k])
        fdist_dict[key] = v

    with open(output_filepath, "w") as output_file:
        json.dump(fdist_dict, output_file)
