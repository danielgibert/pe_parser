import tensorflow as tf
import json


def load_vocabulary(vocabulary_filepath):
    print("ToDo")


def header_asm_sections():
    kown_sections = ['.text','.data','.bss', '.rdata','.edata','.idata', '.rsrc','.tls','.reloc']
    colnames = kown_sections + ['Num_Sections', 'Unknown_Sections', 'Unknown_Sections_lines']
    colnames += ['.text_por','.data_por','.bss_por', '.rdata_por','.edata_por',
                 '.idata_por', '.rsrc_por','.tls_por','.reloc_por']
    colnames += ['known_Sections_por', 'Unknown_Sections_por', 'Unknown_Sections_lines_por']
    return colnames

def header_asm_data_define():
    colnames = ['db_por','dd_por','dw_por','dc_por','db0_por','dbN0_por','dd_text',
                'db_text','dd_rdata','db3_rdata','db3_data','db3_all','dd4','dd5',
                'dd6','dd4_all','dd5_all','dd6_all']
    return colnames

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def load_vocabulary(vocabulary_filepath):
    """
    It reads and stores in a dictionary-like structure the data from the file passed as argument

    Parameters
    ----------
    vocabulary_filepath: str
        JSON-like file

    Return
    ------
    vocabulary_dict: dict
    """
    with open(vocabulary_filepath, "r") as vocab_file:
        vocabulary_dict = json.load(vocab_file)
    return vocabulary_dict

def load_parameters(parameters_path):
    """
    It loads the network parameters

    Parameters
    ----------
    parameters_path: str
        File containing the parameters of the network
    """
    with open(parameters_path, "r") as param_file:
        params = json.load(param_file)
    return params

def serialize_bytes_example(Id, bytes, label):
    """
    Creates a tf.Example message ready to be written to a file
    :param bytes: str -> "00,FF,...,??,NONE"
    :param label: int [0,8]
    :return:
    """
    feature = {
        'Id': _bytes_feature(Id.encode('UTF-8')),
        'bytes': _bytes_feature(bytes.encode('UTF-8')),
        'label': _int64_feature(label)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def serialize_opcodes_example(Id, opcodes, label):
    """
    Creates a tf.Example message ready to be written to a file
    :param opcodes: str -> "push,pop,...,NONE"
    :param label: int [0,8]
    :return:
    """
    feature = {
        'Id': _bytes_feature(Id.encode('UTF-8')),
        'opcodes': _bytes_feature(opcodes.encode('UTF-8')),
        'label': _int64_feature(label)
    }
    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def serialize_structural_entropy_example(Id, structural_entropy, label):
    feature={
        'Id': _bytes_feature(Id.encode('UTF-8')),
        'structural_entropy': _bytes_feature(structural_entropy.tostring()),
        'label': _int64_feature(label)
    }

    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def serialize_grayscale_image_example(Id, img, width, height, label):
    feature={
        'Id': _bytes_feature(Id.encode('UTF-8')),
        'img': _bytes_feature(img.tostring()),
        'width': _int64_feature(width),
        'height': _int64_feature(height),
        'label': _int64_feature(label)
    }

    example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
    return example_proto.SerializeToString()

def create_lookup_table(vocabulary_mapping, num_oov_buckets):
    keys = [k for k in vocabulary_mapping.keys()]
    values = [tf.constant(vocabulary_mapping[k], dtype=tf.int64) for k in keys]

    table = tf.lookup.StaticVocabularyTable(
        tf.lookup.KeyValueTensorInitializer(
            keys=keys,
            values=values
        ),
        num_oov_buckets
    )
    return table

