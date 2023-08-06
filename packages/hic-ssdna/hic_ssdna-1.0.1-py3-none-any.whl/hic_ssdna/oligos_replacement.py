import getopt
import sys

from .bed_assembly import bed_assembly
from .little_functions import problem_in_csv, startend, oligo_positions, not_in_oligo, add_chr_artificial
from .oligofile_correction import oligo_correction


def replacement(input_genome, input_oligos, output_genome, bed_path, flanking_size):
    oligos = oligo_correction(input_oligos)
    if problem_in_csv(oligos):
        print('Error: the csv file structure is not correct, please check the README file')

    position = 0
    position_art = 0
    start, end = startend(0, oligos)
    startart, endart = startend(0, oligos)
    flank = int(flanking_size)
    artificial = ''
    with open(output_genome, 'w') as new_genome:
        new_genome.write('')
    with open(input_genome, 'r') as genome:
        for line in genome:
            if line[0] == '>':
                position = 0
                position_art = 0
                position_oligo = 0
                oligos_positions = oligo_positions(line, oligos)
                oligos_positionsart = oligo_positions(line, oligos)
                k = 0
                kart = 0
                if oligos_positions != [] and oligos_positionsart != []:
                    start, end = startend(oligos_positions[k], oligos)
                    startart, endart = startend(oligos_positionsart[kart], oligos)
                with open(output_genome, 'a') as new_genome:
                    new_genome.write(line)

            elif not_in_oligo(position_art, flank, line, startart, endart, oligos_positionsart):
                with open(output_genome, 'a') as new_genome:
                    new_genome.write(line)
                position += len(line) - 1
                position_art += len(line) - 1

            else:
                for ch in line:
                    if position_art in range(startart - flank, endart + flank) and ch != '\n':
                        artificial += ch
                        position_art += 1

                        if position_art == endart + flank \
                                and kart < len(oligos_positionsart) - 1:

                            kart += 1
                            startart, endart = startend(oligos_positionsart[kart], oligos)

                    elif ch != '\n':
                        position_art += 1

                    if position in range(start, end) and ch != '\n':

                        with open(output_genome, 'a') as new_genome:
                            new_genome.write(oligos['sequence_modified'][oligos_positions[k]][position_oligo])

                        position_oligo += 1
                        position += 1
                        if position == end and k < len(oligos_positions) - 1:
                            position_oligo = 0
                            k += 1
                            start, end = startend(oligos_positions[k], oligos)

                    else:
                        with open(output_genome, 'a') as new_genome:
                            new_genome.write(ch)
                            if ch in ['A', 'T', 'G', 'C', 'N', 'a', 't', 'g', 'c', 'n']:
                                position += 1

    bed_assembly(oligos, flanking_size, bed_path)
    if line[-1] != '\n':
        with open(output_genome, 'a') as new_genome:
            new_genome.write('\n')
    add_chr_artificial(artificial, output_genome)


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print('Please enter arguments correctly')
        exit(0)

    flanking_size = 0
    try:
        opts, args = getopt.getopt(argv, "hi:c:o:b:s:", ["--help", "igenome", "cfile", "ogenome", "bfile", "size"])
    except getopt.GetoptError:
        print('oligos_replacement arguments : \n'
              '-i <fasta_genome_input> \n'
              '-o <fasta_genome_output> \n'
              '-c <csv_oligos_input> \n'
              '-b <bed_output> \n'
              '-r <flanking_sizes> (int)\n')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('oligos_replacement arguments : -i <fasta_genome_input> -o <fasta_genome_output>'
                  ' -c <csv_oligos_input> -b <bed_output> -r ''<flanking_sizes>')
            sys.exit()
        elif opt in ("-i", "--igenome"):
            input_genome_path = arg
        elif opt in ("-o", "--ogenome"):
            output_genome_path = arg
        elif opt in ("-c", "--cfile"):
            input_oligos_path = arg
        elif opt in ("-b", "--bfile"):
            output_bed_path = arg
        elif opt in ("-s", "size"):
            flanking_size = arg

    replacement(input_genome_path, input_oligos_path, output_genome_path, output_bed_path, flanking_size)


if __name__ == "__main__":
    main(sys.argv[1:])
