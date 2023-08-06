import pandas as pd


def oligo_correction_cut(input_oligos):
    oligos = pd.read_csv(input_oligos, sep=",")
    oligos.columns = [oligos.columns[i].lower() for i in range(len(oligos.columns))]

    # delete lines that are not 'ss' or 'ss_neg' type
    # for j in range(len(oligos)):
    #     if oligos['type'][j] != 'ss' and oligos['type'][j] != 'ss_neg':
    #         oligos.drop([j], inplace=True)

    oligos.reset_index(drop=True, inplace=True)
    oligos = oligos.sort_values(by=['chr', 'start'])
    oligos.reset_index(drop=True, inplace=True)

    return oligos


def bed_artificial(input_bed):  # from the initial bed, filter and return df with only oligos in chr_art
    bed = pd.read_csv(input_bed, sep='\t', header=None)
    for k in range(len(bed)):
        if bed[0][k] != 'chr_art' or 'flank' in bed[3][k]:
            bed.drop([k], inplace=True)
            index = [p for p in range(len(bed))]
    bed.set_index(pd.Index(index), inplace=True)
    return bed


def bed_genome(input_bed):  # from the initial bed, filter and return df with only oligos in genome chromosomes
    bed = pd.read_csv(input_bed, sep='\t', header=None)
    for k in range(len(bed)):
        if bed[0][k] == 'chr_art' or 'flank' in bed[3][k]:
            bed.drop([k], inplace=True)
            index = [p for p in range(len(bed))]
    bed.set_index(pd.Index(index), inplace=True)
    return bed


def cut_chr_art(input_oligos, input_bed):
    oligos = pd.read_csv(input_oligos, sep=",")
    oligos_ss = oligo_correction_cut(input_oligos)
    bed_art = bed_artificial(input_bed)
    bed_gen = bed_genome(input_bed)
    if len(bed_art) != len(bed_gen):
        print("Error: there is a problem in the bed file (not same number of coordinates in genome and chr_art")
        pass

    for k in range(len(bed_art)):
        start_art, end_art = bed_art[1][k], bed_art[1][k]
        start_gen, end_gen = bed_gen[1][k], bed_gen[1][k]
        start_capt, end_capt = oligos_ss['start'][k], oligos_ss['end'][k]

        new_start = start_art + start_capt - start_gen
        new_end = end_art + end_capt - end_gen

        df = pd.DataFrame([['chr_art', new_start, new_end, oligos_ss['type'][k], oligos_ss['name'][k], '']],
                          columns=['chr', 'start', 'end', 'type', 'name', 'sequence'])

        oligos = pd.concat([oligos, df])
        print(new_end-new_start == end_capt-start_capt)
    return oligos


oligo_path = '/scratch/lanani/Stage L3/Projet/Pycharm/inputs/capture_oligo_positions_modified.csv'
bed_path = '/scratch/lanani/Stage L3/Projet/Pycharm/outputs/chr_articial_coordinates.bed'

# print(bed_genome(bed_path))
# print(bed_artificial(bed_path))


new_oligos = cut_chr_art(oligo_path, bed_path)

new_oligos.to_csv('/scratch/lanani/Stage L3/Projet/Pycharm/outputs/new_capture_oligos.csv', index=False)
# oligos_path = '/scratch/lanani/Stage L3/' \
# 'Projet/Pycharm/inputs/capture_oligo_positions_modified.csv'
#
# print(oligo_correction_cut(oligo_path))
