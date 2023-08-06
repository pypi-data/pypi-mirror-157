def startend(num_oligo, dataframe):
    start = dataframe['start'][num_oligo] - 1
    end = dataframe['end'][num_oligo]
    return start, end


def oligo_positions(line, dataframe):  # finds oligos positions in the csv file of the chromosome name of the line
    L = []
    for k in range(len(dataframe)):
        name = dataframe['chr'][k]
        n = len(name) # chromosome name length
        if ' ' in name:
            print("Error: There is a space ' ' in the chomosomes names in the csv oligios file."
                  " The chromosome name has to be without space ' '.")
            break
        if name in line and line[n+1] in (' ', '\n'):
            L.append(k)
    return L


def problem_in_csv(dataframe):
    line = list(dataframe.columns)
    if 'chr' not in line or 'start' not in line or 'end' not in line or \
            'sequence_modified' not in line or 'sequence_original' not in line\
            or 'name' not in line or 'type' not in line:
        return True


def not_in_oligo(position_art, reads_size, line, startart, endart, oligos_positionsart):
    if oligos_positionsart == [] \
            or position_art < startart - 2 * len(line) - reads_size \
            or position_art > endart + 2 * len(line) + reads_size:
        return True


def add_chr_artificial(artificial, output_genome):
    with open(output_genome, 'r') as new_genome:
        new_genome.readline()
        line = new_genome.readline()
        long = len(line) - 1

    n = 0
    with open(output_genome, 'a') as new_genome:
        new_genome.write(">chr_art  " + '(' + str(len(artificial)) + ' bp)' + "\n")
        while n < len(artificial):
            if n + long > len(artificial):
                new_genome.write(artificial[n:])
                new_genome.write('\n')
                n += long
            else:
                new_genome.write(artificial[n:n + long] + '\n')
                n += long
