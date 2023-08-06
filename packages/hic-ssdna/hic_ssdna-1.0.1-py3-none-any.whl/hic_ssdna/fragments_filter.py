import pandas as pd


def oligos_correction(oligos_path):
    oligos = pd.read_csv(oligos_path, sep=",")
    oligos.columns = [oligos.columns[i].lower() for i in range(len(oligos.columns))]
    oligos.sort_values(by=['chr', 'start'], inplace=True)
    oligos.reset_index(drop=True, inplace=True)

    return oligos


def fragments_correction(fragments_path):
    fragments = pd.read_csv(fragments_path, sep='\t')
    fragments = pd.DataFrame({'frag': [k for k in range(len(fragments))],
                              'chr': fragments['chrom'],
                              'start': fragments['start_pos'],
                              'end': fragments['end_pos'],
                              'size': fragments['size'],
                              'gc_content': fragments['gc_content']
                              })

    return fragments


def starts_match(fragments, oligos_path):
    # if the capture oligos is in a fragments, it changes the start of
    # the oligos dataframe to match with the fragments starts
    oligos = oligos_correction(oligos_path)
    L_starts = []
    for i in range(len(oligos)):
        oligos_chr = oligos['chr'][i]
        middle = int((oligos['end'][i] - oligos['start'][i] - 1) / 2 + oligos['start'][i] - 1)
        if oligos_chr == 'chr_artificial':
            for k in reversed(range(len(fragments))):
                interval = range(fragments['start'][k], fragments['end'][k])
                fragments_chr = fragments['chr'][k]
                if middle in interval and fragments_chr == oligos_chr:
                    L_starts.append(fragments['start'][k])
                    break
        else:
            for k in range(len(fragments)):
                interval = range(fragments['start'][k], fragments['end'][k])
                fragments_chr = fragments['chr'][k]
                if middle in interval and fragments_chr == oligos_chr:
                    L_starts.append(fragments['start'][k])
                    break
    oligos['start'] = L_starts
    return oligos


def pre_filtering(fragments_path, oligos_path):

    fragments = fragments_correction(fragments_path)
    oligos = starts_match(fragments, oligos_path)
    oligos.set_index(['chr', 'start'])
    oligos.pop("end")
    fragments.set_index(['chr', 'start'])
    fragments_filtered = fragments.merge(oligos, on=['chr', 'start'])
    fragments_filtered.sort_values(by=['chr', 'start'])
    return fragments_filtered, oligos


# oligo_path = '/Users/loqmenanani/OneDrive/ENS/L3_ENS/Stage_L3/Projet_cbp/Pycharm/outputs/' \
#              'new_capture_oligos.csv'
# fragments_paths = '/Users/loqmenanani/OneDrive/ENS/L3_ENS/Stage_L3/Projet_cbp/Pycharm/inputs/fragments_list.txt'
# contacts_paths = '/Users/loqmenanani/OneDrive/ENS/L3 ENS/Stage L3/Projet ' \
#                  'cbp/Pycharm/inputs/abs_fragments_contacts_weighted.txt'
#
# output_path = '/Users/loqmenanani/OneDrive/ENS/L3_ENS/Stage_L3/Projet_cbp/Pycharm/outputs/pre_filtering.txt'

# oligo_path = '/scratch/lanani/Stage_L3_cbp/Projet/Pycharm/outputs/new_capture_oligos.csv'
# fragments_paths = '/scratch/lanani/Stage_L3_cbp/Projet/Pycharm/inputs/fragments_list.txt'
# contacts_paths = '/scratch/lanani/Stage_L3_cbp/Projet/Pycharm/inputs/abs_fragments_contacts_weighted.txt'
# output_path = '/scratch/lanani/Stage_L3_cbp/Projet/Pycharm/outputs/fragments_filtered.csv'
#
# a, b = pre_filtering(fragments_paths, oligo_path)
# a.to_csv(output_path)
