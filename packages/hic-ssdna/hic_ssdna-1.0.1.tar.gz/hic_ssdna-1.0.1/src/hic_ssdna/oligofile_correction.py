import pandas as pd
pd.options.mode.chained_assignment = None


def reverse_complement(dna):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'a': 't', 'c': 'g', 'g': 'c', 't': 'a', 'n': 'n', 'N': 'N'}
    return ''.join([complement[base] for base in dna[::-1]])


def oligo_correction(input_oligos):
    oligos = pd.read_csv(input_oligos, sep=",")
    oligos.columns = [oligos.columns[i].lower() for i in range(len(oligos.columns))]

    # delete lines that are not 'ss' or 'ss_neg' type
    for j in range(len(oligos)):
        if oligos['type'][j] != 'ss' and oligos['type'][j] != 'ss_neg':
            oligos.drop([j], inplace=True)

    oligos.reset_index(drop=True, inplace=True)
    oligos = oligos.sort_values(by=['chr', 'start'])
    oligos.reset_index(drop=True, inplace=True)

    for k in range(len(oligos)):

        if oligos['orientation'][k] == 'C':
            oligos['orientation'][k] = 'W'

            original = oligos['sequence_original'][k]
            oligos['sequence_original'][k] = reverse_complement(original)

            modified = oligos['sequence_modified'][k]
            modified = modified.upper()
            oligos['sequence_modified'][k] = reverse_complement(modified)

        elif oligos['orientation'][k] == 'W':
            modified = oligos['sequence_modified'][k]
            modified = modified.upper()
            oligos['sequence_modified'][k] = str(modified)

    return oligos


# input_path = '/scratch/lanani/Stage L3/Projet/Pycharm/inputs/new_capture_oligos.csv'
# output_path = '/scratch/lanani/Stage L3/Projet/Pycharm/outputs/new_capture_oligos.csv'

# input_path = '/Users/loqmenanani/OneDrive/ENS/L3 ENS/Stage L3/Projet cbp/Pycharm/inputs/oligo_positions_modified.csv'
# output_path = '/Users/loqmenanani/OneDrive/ENS/L3 ENS/Stage L3/Projet cbp/Pycharm/inputs/test_oligos.csv'
#
# a = oligo_correction(input_path)
# print(a)
# a.to_csv(output_path, sep=',')
# print(oligo_correction(oligo_path))
