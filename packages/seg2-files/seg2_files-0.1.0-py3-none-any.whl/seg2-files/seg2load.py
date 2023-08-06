"""
This is a simple program for reading binary SEG-2 format seismic/radar data into a header dictionary
and a numpy array containing trace data. 

This code was originally inspired by a MATLAB script, seg2load.m, with the following attribution:

Modified  by Vilhelm, Charles University, Prague in october 2002
from original by Pièce PY 24/07/1996;LAMI - DeTeC Demining Technology Center;
Swiss Federal Institute of Technology (EPFL) - Lausanne, Switzerland

However, this code in its current incarnation has diverged almost entirely and is not really a port.

Nathan Stoikopoulos
University of Toronto
January 2022
"""

import struct
import numpy as np


def __check_block_id(descriptor, check_id, error_message):
    """
    Ensures that block id number matches that specified in check_id, and
    determines byte order (endianness) of file
    :param byte[] descriptor: bytes in file/trace descriptor block
    :param byte check_id:     number against which block id is checked.
                              0x3a55 / 0x553a for file descriptor
                              0x4422 / 0x2244 for trace descriptor
    :param str error_message: Error message to display if id does not match

    :return str endian:       Byte order of file. '>' for big-endian,
                              '<' for little endian
    """

    block_id = struct.unpack('h', descriptor[0:2])[0]
    if block_id == check_id:
        endian = '<'
    else:
        if struct.unpack('>h', descriptor[0:2])[0] == check_id:
            endian = '>'
        else:
            raise Exception(error_message)
    return endian


def __start_descriptor(byte_array, check_id, error_message, cursor,
                       descriptor_size):
    """
    Begins reading descriptor block by checking block id, returning descriptor
     block bytes and advancing byte cursor to beginning of free strings
    :param byte[] byte_array: Bytes from file
    :param byte check_id: Block id which will be checked
    :param str error_message: Message if block id check fails
    :param int cursor: Current byte being read
    :param int descriptor_size: Size of file/trace descriptor in bytes
    :return byte[]:

    """
    descriptor = byte_array[cursor:cursor + descriptor_size]
    cursor += descriptor_size
    byte_order = __check_block_id(descriptor, check_id, error_message)
    return descriptor, cursor, byte_order


def __get_block_size(byte_array, index, prepend='', mode='H'):
    """
    Determines maximum size of following block. Not all bytes in block
    are necessarily used
    :param byte[] byte_array: Bytes from file
    :param index:
    :param prepend:
    :param mode:
    :return:
    """
    word_size = {'H': 2, 'L': 4}
    block_size = struct.unpack(prepend + mode,
                               byte_array[index:index + word_size[mode]])[0]
    return block_size


def __read_offset(byte_array, index, prepend=''):
    offset = __get_block_size(byte_array, index) - 2
    return offset, index+2


def __descriptor_to_dict(freestr_bin, descriptor_dict, binary=True):
    if binary:
        freestr_string = ''.join([fs.decode('utf8') for fs in freestr_bin])
    else:
        freestr_string = freestr_bin
    freestr_parts = str(freestr_string).split(' ')
    key = freestr_parts[0]
    value = ' '.join(freestr_parts[1:])
    descriptor_dict[key] = value
    return key, value


def __read_free_strings(free_string_bytes, out_dict, index, string_term, line_term, prepend):
    freestr = b''
    while string_term not in freestr:
        offset, index = __read_offset(free_string_bytes, index)
        freestr = struct.unpack(prepend + (offset - 1) * 's',
                                free_string_bytes[index:index + offset - 1])
        name, notes = __descriptor_to_dict(freestr, out_dict)

        if name == 'NOTE':
            note_dict = {}
            for line in notes.split(line_term + ' ')[1:]:
                # Strip removes spurious characters on last line of block
                __descriptor_to_dict(line.strip(' ' + 2 * line_term +
                                                string_term.decode('utf8')),
                                     note_dict,
                                     binary=False)
            out_dict[name] = note_dict
            index += 3

        index += offset
    return index


def __read_file_descriptor(file_bytes, header_dict, index, descriptor_size):
    file_desc, index, byte_order = __start_descriptor(file_bytes, 0x3a55,
                                                      'Not a SEG2 file!',
                                                      index, descriptor_size)
    # currently not used
    revision_number = struct.unpack(byte_order+'h', file_desc[2:4])

    # Maximum size in bytes of pointers to trace data - not necessarily all used
    trace_pointer_size = __get_block_size(file_bytes, 4, byte_order)
    if not (4 <= trace_pointer_size <= 65532) and (trace_pointer_size % 4 != 0):
        raise ValueError('Invalid Trace Pointer Sub-block size!')

    # Actual number of traces. Size of trace pointer information is 4 times this
    num_traces = __get_block_size(file_bytes, 6, byte_order)
    if not (1 <= num_traces <= trace_pointer_size / 4):
        raise ValueError('Invalid number of traces!')

    # Line and free string block terminating characters
    # Line term is used as a string since it occurs within strings
    string_term = struct.unpack(byte_order+'cc', file_desc[9:11])[0]
    line_term = struct.unpack(byte_order+'cc',
                              file_desc[12:14])[0].decode('utf8')

    # Get pointers to traces
    trace_pointers = struct.unpack(byte_order+str(num_traces)+'L',
                                   file_bytes[index:index + 4*num_traces])
    index += trace_pointer_size

    index = __read_free_strings(file_bytes, header_dict, index, string_term,
                                line_term, byte_order)

    return index, byte_order, trace_pointers, line_term, string_term


def __read_trace_descriptor(byte_array, header_dict, index, descriptor_size, line_term, string_term):
    old_index = index
    trace_desc, index, byte_order = __start_descriptor(byte_array, 0x4422,
                                                       'Not a trace descriptor!',
                                                       index, descriptor_size)
    desc_block_size = __get_block_size(trace_desc, 2, byte_order)
    data_block_size = __get_block_size(trace_desc, 4, byte_order, 'L')
    num_samples = __get_block_size(trace_desc, 8, byte_order, 'L')
    data_types = {1: 'fixed16', 2: 'fixed32', 3: 'SEG-D 20', 4: np.float32,
                  5: np.float64}
    dtype_byte = struct.unpack(byte_order+'b', trace_desc[12:13])[0]
    if dtype_byte in [1, 2, 3]:
        raise NotImplementedError('Fixed point formats are not currently'
                                  ' supported')
    dtype = data_types[dtype_byte]
    index = __read_free_strings(byte_array, header_dict, index, string_term,
                                line_term, byte_order)

    return old_index + desc_block_size + 1, dtype, num_samples


def __read_trace_data(byte_array, index, num_samples, byte_order, dtype):
    dt = np.dtype(dtype)
    dt.newbyteorder(byte_order)
    trace = np.frombuffer(byte_array, dtype=dtype, count=num_samples, offset=index).T
    return trace


def gain(gain_string):
    return float(gain_string.split(' ')[0])


def seg2_load(filename):

    with open(filename, 'rb') as file:
        file_bytes = file.read()

    header = {'rec': {}, 'tr': {}}  # initialize header
    descriptor_size = 32  # In bytes. Can vary, SEG2 standard is 32
    cursor = 0  # current byte number being read

    cursor, byte_order, trace_pointers, line_term, string_term = \
        __read_file_descriptor(file_bytes, header['rec'], cursor, descriptor_size)
    trace_descriptors = []
    traces = []
    for i, pointer in enumerate(trace_pointers):
        cursor = pointer
        trace_descriptors.append({})
        cursor, dt, num_samples = __read_trace_descriptor(file_bytes, trace_descriptors[i], cursor, descriptor_size,
                                                          line_term, string_term)
        traces.append(__read_trace_data(file_bytes, cursor - 1, num_samples, byte_order, dt))
    trace_array = np.array(traces).T

    def filter_tuple(filter_string):
        return np.array(list(map(float, filter_string.split(' '))))

    # Functions used to convert each trace descriptor field into a usable format
    trace_var_funs = {'ALIAS_FILTER': filter_tuple,
                      'AMPLITUDE_RECOVERY': str,
                      'BAND_REJECT_FILTER': filter_tuple,
                      'CDP_NUMBER': int,
                      'CDP_TRACE': int,
                      'CHANNEL_NUMBER': int,
                      'DATUM': float,
                      'DELAY': float,
                      'DESCALING_FACTOR': float,
                      'DIGITAL_BAND_REJECT_FILTER': filter_tuple,
                      'DIGITAL_HIGH_CUT_FILTER': filter_tuple,
                      'DIGITAL_LOW_CUT_FILTER': filter_tuple,
                      'END_OF_GROUP': bool,
                      'FIXED_GAIN': gain,
                      'HIGH_CUT_FILTER': filter_tuple,
                      'LINE_ID': str,
                      'LOW_CUT_FILTER': filter_tuple,
                      'NOTCH_FREQUENCY': float,
                      'POLARITY': int,
                      'RAW_RECORD': str,
                      'RECEIVER': str,
                      'RECEIVER_GEOMETRY': filter_tuple,
                      'RECEIVER_LOCATION': filter_tuple,
                      'RECEIVER_SPECS': str,
                      'RECEIVER_STATION_NUMBER': int,
                      'SAMPLE_INTERVAL': float,
                      'SHOT_SEQUENCE_NUMBER': int,
                      'SKEW': float,
                      'SOURCE': str,
                      'SOURCE_GEOMETRY': filter_tuple,
                      'SOURCE_LOCATION': filter_tuple,
                      'SOURCE_STATION_NUMBER': int,
                      'STACK': int,
                      'STATIC_CORRECTIONS': filter_tuple,
                      'TRACE_TYPE': str,
                      'NOTE': str }

    for key in trace_descriptors[0]:
        var_fun = trace_var_funs[key]
        header['tr'][key] = np.array(list(map(var_fun,
                                     [td[key] for td in trace_descriptors])))
    return trace_array, header
