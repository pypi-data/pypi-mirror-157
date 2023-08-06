from .little_functions import startend


def chr_name_bed(oligos, num_oligo):
    return oligos['chr'][num_oligo]


def bed_assembly(oligos, reads_sizes, bedpath):

    with open(bedpath, 'w') as bed:

        if reads_sizes == 0:
            n_cum = 1
            for k in range(len(oligos)):
                start, end = startend(k, oligos)
                start += 1
                oligo_name = '\t' + oligos['name'][k]
                n = len(oligos['sequence_original'][k])
                bed.write(chr_name_bed(oligos, k) + '\t' + str(start) + '\t' +
                          str(end) + oligo_name + '\n')
                n_cum += n

            n_cum = 1
            for k in range(len(oligos)):
                n = len(oligos['sequence_original'][k])
                oligo_name = '\t' + oligos['name'][k]
                bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                          str(n_cum + n - 1) + oligo_name + '\n')
                n_cum += n
        else:
            n_cum = 1
            # genome
            for k in range(len(oligos)):
                oligo_name = '\t' + oligos['name'][k]
                start, end = startend(k, oligos)
                start += 1
                n = len(oligos['sequence_original'][k])
                # flank 5'

                if start == 1:
                    pass
                elif start - reads_sizes <= 0:
                    bed.write(chr_name_bed(oligos, k) + '\t1\t' + str(start) +
                              oligo_name + "_flank_5'" + '\n')
                elif k > 0 and start - reads_sizes < oligos['end'][k - 1]:
                    pass
                else:
                    bed.write(chr_name_bed(oligos, k) + '\t' + str(start - reads_sizes) + '\t' +
                              str(start - 1) + oligo_name + "_flank_5'" + '\n')
                    n_cum += reads_sizes

                # oligo
                bed.write(chr_name_bed(oligos, k) + '\t' + str(start) + '\t' +
                          str(end) + oligo_name + '\n')

                n_cum += n

                # flank 3'
                if k + 1 != len(oligos) and end + reads_sizes >= oligos['start'][k + 1] \
                        and chr_name_bed(oligos, k) == chr_name_bed(oligos, k + 1):
                    bed.write(chr_name_bed(oligos, k) + '\t' + str(end + 1) + '\t' +
                              str(oligos['start'][k + 1] - 1) + oligo_name + "_flank_3'" + '\n')
                    bed.write(chr_name_bed(oligos, k) + '\t' + str(end + 1) + '\t' +
                              str(oligos['start'][k + 1] - 1) + '\t' + oligos['name'][k + 1] + "_flank_5'" + '\n')

                    n_cum += reads_sizes
                else:
                    bed.write(chr_name_bed(oligos, k) + '\t' + str(end + 1) + '\t' +
                              str(end + reads_sizes) + oligo_name + "_flank_3'" + '\n')
                    n_cum += reads_sizes

            # artificial

            n_cum = 1
            for k in range(len(oligos)):
                oligo_name = '\t' + oligos['name'][k]
                start, end = startend(k, oligos)
                start += 1
                n = len(oligos['sequence_original'][k])

                # flank 5'
                if start == 1:
                    pass
                elif start - reads_sizes < 0:
                    bed.write('chr_art' + '\t1\t' + str(start - 1) + oligo_name + "_flank_5'" + '\n')
                    n_cum += start
                elif k > 0 and start - reads_sizes < oligos['end'][k - 1]:
                    pass
                else:
                    bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                              str(n_cum + reads_sizes - 1) + oligo_name + "_flank_5'" + '\n')
                    n_cum += reads_sizes

                bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                          str(n_cum + n - 1) + oligo_name + '\n')
                n_cum += n

                if k + 1 != len(oligos) and end + reads_sizes >= oligos['start'][k + 1] \
                        and chr_name_bed(oligos, k) == chr_name_bed(oligos, k + 1):
                    new_reads_sizes = reads_sizes
                    while k + 1 != len(oligos) and end + new_reads_sizes >= oligos['start'][k + 1]:
                        new_reads_sizes -= 1
                    bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                              str(n_cum + new_reads_sizes - 1) + oligo_name + "_flank_3'" + '\n')
                    bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                              str(n_cum + new_reads_sizes - 1) + '\t' + oligos['name'][k + 1] + "_flank_5'" + '\n')
                    n_cum += new_reads_sizes

                else:
                    bed.write('chr_art' + '\t' + str(n_cum) + '\t' +
                              str(n_cum + reads_sizes - 1) + oligo_name + "_flank_3'" + '\n')
                    n_cum += reads_sizes
