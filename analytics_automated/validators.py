import imghdr
import re
from collections import Counter


def gif(file_data):
    if 'gif' in imghdr.what('', file_data):
        return True
    else:
        return False


def png(file_data):
    if 'png' in imghdr.what('', file_data):
        return True
    else:
        return False


def jpeg(file_data):
    if 'jpeg' in imghdr.what('', file_data):
        return True
    else:
        return False


def pdb_file(file_data):
    string_data = file_data.decode("utf-8")
    pdb_pattern = re.compile("ATOM\s+\d+", re.IGNORECASE)
    if re.search(pdb_pattern, string_data):
        # print("yay")
        return True
    else:
        # print("boo")
        return False


def __test_seq(seq):
    # dealing with single sequences here
    counters = Counter(seq)
    nucleotideSum = counters['A']+counters['T']+counters['C'] + \
        counters['G']+counters['U']+counters['N'] + \
        counters['a']+counters['t']+counters['c'] + \
        counters['g']+counters['u']+counters['n']
    if nucleotideSum/len(seq) >= 0.95:
        return False  # false if it is probably nucleotide

    char_check = re.compile(r'[^ACDEFGHIKLMNPQRSTVWYX_-]+', re.IGNORECASE)
    if bool(re.search(char_check, seq)):
        return False  # false if non-amino acid characters are present

    return True


def seq(file_data):
    string_data = file_data.decode("utf-8")
    header_count = string_data.count(">")
    lines = string_data.splitlines()

    if header_count <= 1:
        lines = [x for x in lines if not x.startswith(('>', ';'))]
        if len(lines) < 1:  # false if no sequences
            return False
        seq = ''.join(lines)
        return __test_seq(seq)
    else:
        seq_count = 0
        residue_count = 0
        seqs = {}
        for line in lines:
            if line.startswith('>'):
                seq_count += 1
                seqs[seq_count] = ''
            else:
                seqs[seq_count] += line
                residue_count += len(line)
        msa_residue_total = len(seqs[1])*seq_count
        if not residue_count == msa_residue_total:
            return False

        for k, v in seqs.items():
            if not __test_seq(v):
                return False

        return True
