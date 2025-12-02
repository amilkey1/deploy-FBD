import subprocess as sub
import sys,os,re,math,shutil,random
import copydata, setupsubst, setupmain

# scriptdir = os.path.dirname(os.path.realpath(sys.argv[0]))

def calcDimRowCol(rep, nreps):
    # If nreps = 9, then the grid is 3x3, where dim = sqrt(nreps) = 3
    # 
    # Assuming 
    #   x_min  = 0.001, x_max = 0.201, x_max - x_min = 0.200
    #   y_min = 0.100,  y_max = 1.100, y_max - y_min = 1.000
    #
    # rep  | row  = (rep-1)/3  |  col  = (rep-1)%3  |       x =   min + row*(max-min)/(dim-1) |      y = min + col*(max-min)/(dim-1) |
    #   1  |   0  =       0/3  |   0   =       0%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   | 
    #   2  |   0  =       1/3  |   1   =       1%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   3  |   0  =       2/3  |   2   =       2%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |
    #   4  |   1  =       3/3  |   0   =       3%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   |
    #   5  |   1  =       4/3  |   1   =       4%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   6  |   1  =       5/3  |   2   =       5%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |
    #   7  |   2  =       6/3  |   0   =       6%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   |
    #   8  |   2  =       7/3  |   1   =       7%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   9  |   2  =       8/3  |   2   =       8%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |

    dim = math.sqrt(nreps)    
    row = (rep-1)//dim
    col = (rep-1)%dim
        
    return (dim,row,col)

def readNexusFile(fn):
    '''
    Reads nexus file whose name is specified by fn and returns ntax, nchar, taxa, and a
    sequences dictionary with taxon names as keys. The values ntax and nchar are integers,
    while taxa is a list of taxon names in the order they were found in the taxa block or
    data block. Any underscores in taxon names are converted to spaces before being saved
    in the taxa list or as a key in the sequences dictionary. Also all nexus comments
    (text in square brackets) will be ignored.
    '''
    stuff = open(fn, 'r').read()
    mask = None

    # determine if taxa block exists
    taxa_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:TAXA|Taxa|taxa)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        taxa_block = m.group(1).strip()

    # determine if characters block exists
    characters_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:CHARACTERS|Characters|characters)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        characters_block = m.group(1).strip()

    # determine if data block exists
    data_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:DATA|Data|data)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        data_block = m.group(1).strip()

    if data_block is not None:
        # get ntax and nchar
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NTAX|ntax|Ntax|NTax)\s*=\s*(\d+)\s+(?:NCHAR|nchar|Nchar|NChar)\s*=\s*(\d+)\s*;', data_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in data block'
        ntax = int(m.group(1))
        nchar = int(m.group(2))

        # get matrix
        m = re.search(r'(?:MATRIX|matrix|Matrix)\s+(.+?)\s*;', data_block, re.M | re.S)
        assert m, 'Could not decipher matrix statement in data block'
        lines = m.group(1).strip().split('\n')
        taxa = []
        sequences = {}
        for line in lines:
            m = re.match(r'\[([-*]+)\]', line.strip())
            if m is not None:
                mask = m.group(1)
            else:
                stripped_line = re.sub(r'\[.+?\]', '', line).strip()
                if len(stripped_line) > 0:
                    parts = line.split()
                    assert len(parts) == 2, 'Found more than 2 parts to this line:\n%s' % line
                    taxon_name = re.sub(r'_', ' ', parts[0]).strip()
                    taxa.append(taxon_name)
                    sequences[taxon_name] = parts[1]
    else:
        assert characters_block is not None and taxa_block is not None, 'Assuming nexus file contains either a data block or a taxa block and characters block'

        # get ntax from taxa block
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NTAX|ntax|Ntax|NTax)\s*=\s*(\d+)\s*;', taxa_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in taxa block'
        ntax = int(m.group(1))

        # get nchar from characters block
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NCHAR|nchar|Nchar|NChar)\s*=\s*(\d+)\s*;', characters_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in characters block'
        nchar = int(m.group(1))

        # get matrix from characters block
        m = re.search(r'(?:MATRIX|matrix|Matrix)\s+(.+?)\s*;', characters_block, re.M | re.S)
        assert m, 'Could not decipher matrix statement in characters block'
        lines = m.group(1).strip().split('\n')
        taxa = []
        sequences = {}
        for line in lines:
            m = re.match(r'\[([-*]+)\]', line.strip())
            if m is not None:
                mask = m.group(1)
            else:
                stripped_line = re.sub(r'\[.+?\]', '', line).strip()
                if len(stripped_line) > 0:
                    parts = stripped_line.split()
                    assert len(parts) == 2, 'Found more than 2 parts to this line:\n%s' % line
                    taxon_name = re.sub(r'_', ' ', parts[0]).strip()
                    taxa.append(taxon_name)
                    sequences[taxon_name] = parts[1]

    return (ntax, nchar, mask, taxa, sequences)

def writeFASTAFile(fn, ntax, nchar, taxa, sequences):
    if os.path.exists(fn):
        os.rename(fn, '%s.bak' % fn)
    longest = max([len(t) for t in taxa])
    taxonfmt = '  %%%ds' % longest
    f = open(fn, 'w')
    for t in taxa:
        taxon_name = re.sub(r'\s+', '_', t)
        f.write('> %s\n' % taxon_name)
        f.write('%s\n' % sequences[t])
    f.close()
    
def writeNexusFile(fn, ntax, nchar, mask, taxa, sequences):
    if os.path.exists(fn):
        os.rename(fn, '%s.bak' % fn)
    longest = max([len(t) for t in taxa])
    taxonfmt = '  %%%ds' % longest
    f = open(fn, 'w')
    f.write('#nexus\n\n')
    f.write('begin data;\n')
    f.write('  dimensions ntax=%d nchar=%d;\n' % (ntax, nchar))
    f.write('  format datatype=dna gap=-;\n')
    f.write('  matrix\n')
    if mask is not None:
        f.write(taxonfmt % ' ')
        f.write('[%s]\n' % mask)
    for t in taxa:
        taxon_name = re.sub(r'\s+', '_', t)
        f.write(taxonfmt % taxon_name)
        f.write(' %s\n' % sequences[t])
    f.write('  ;\n')
    f.write('end;\n')
    f.close()
    
def run(rep, nreps, maindir, repdir, rnseed):
    print('  setting up rep %d in directory "%s/%s"' % (rep, maindir, repdir))
    
    refinfof = open(os.path.join(maindir, repdir,'rep-info.txt'),'w')
    
    #############################################
    # Init random number generator for choosing #
    # number of sites and aspects of rate het.  #
    #############################################
    random.seed(rnseed)
    
    ###############################################
    # Get paths to all subdirs for this replicate #
    ###############################################
    
    inner_simdir       = os.path.join(repdir, 'sim')
    inner_smcdir       = os.path.join(repdir, 'smc')
            
    outer_simdir       = os.path.join(maindir, inner_simdir)
    outer_smcdir       = os.path.join(maindir, inner_smcdir)
            
    ##################################
    # Determine row and col from rep #
    ##################################
    dim, row, col = calcDimRowCol(rep, nreps)
        
    #######################################################
    # Determine true speciation and extinction rate  #
    #######################################################
    # Grid has x = extinction rate (mu) and y = speciation rate (i.e. lambda)
    if nreps == 1:
         extinction_rate      = (setupmain.mu_min + setupmain.mu_max)/2.0
         speciation_rate = (setupmain.lambda_min + setupmain.lambda_max)/2.0
    else:
        extinction_rate      =  setupmain.mu_min + row*(setupmain.mu_max  - setupmain.mu_max)/(dim-1)
        speciation_rate = setupmain.lambda_min + col*(setupmain.lambda_max - setupmain.lambda_min)/(dim-1)
            
    
    ##############################
    # Set up the "sim" directory #
    ##############################
    infile  = os.path.join(outer_simdir, '%s-smctree.conf' % setupmain.user)
    outfile = infile
    
    # Create data partitioning and specify relative rates
    subset_info = []
    site_cursor = 1
    subsets = ''
    relrates = ''
    
    # Choose the number of loci for this simulation
    nloci = random.randint(setupmain.min_n_loci, setupmain.max_n_loci)
    if setupmain.user == 'aam21005':
         relrates += 'relative_rates = '
    for g in range(nloci):
        locus = g + 1

        # Choose the number of sites for this locus 
        nsites_this_locus = random.randint(setupmain.min_sites_per_locus, setupmain.max_sites_per_locus)
        first = site_cursor
        last  = site_cursor + nsites_this_locus - 1
        subsets += 'subset = locus%d[nucleotide]:%d-%d\n' % (locus,first,last)

        # Choose the relative rate for this locus 
        relrate_this_locus = random.gammavariate(setupmain.subset_relrate_shape, setupmain.subset_relrate_scale)
        if setupmain.user == 'aam21005':
            if g == 0:
                relrates += str(relrate_this_locus)
            else:
                relrates += ", " + str(relrate_this_locus)

        # Save information about this locus in subset_info vector
        subset_info.append({'locus':locus, 'relrate':relrate_this_locus, 'nsites':nsites_this_locus, 'first':first, 'last':last})

        # Save information about this locus to rep info file
        refinfof.write('\nlocus%d:\n' % locus)
        refinfof.write('  relrate = %g\n' % relrate_this_locus)
        refinfof.write('  nsites  = %d\n' % nsites_this_locus)
        refinfof.write('  first   = %d\n' % first)
        refinfof.write('  last    = %d\n' % last)
        refinfof.flush()

        site_cursor += nsites_this_locus

    if setupmain.user == 'aam21005':
         relrates += '\n'

    # Define number of species and number of individuals for each species
    nspecies = len(setupmain.species) 
    if setupmain.user == 'aam21005':
        species = 'nspecies = %d\n' % nspecies
        species += '\n'

    if setupmain.user == "aam21005":
         setupsubst.substitutions({
             '__RNSEED__':        rnseed, 
             '__MU__':             extinction_rate, 
             '__LAMBDA__':        speciation_rate,
             '__SUBSETS__':       subsets,
             }, infile, outfile)
         os.rename(outfile, os.path.join(outer_simdir, 'smctree.conf'))

    ##############################################################
    # Run simulation program to simulate data for this replicate #
    ##############################################################
    completed_process = sub.run([setupmain.simulator_path], cwd=outer_simdir, capture_output=True, text=True)
    if completed_process.returncode != 0:
        print('\nreturncode: ', completed_process.returncode)
        print('\nstderr: ', completed_process.stderr)
        print('\nstdout: ', completed_process.stdout)
        sys.exit('Aborted.')
    else:
        stdoutput = str(completed_process.stdout)
        open(os.path.join(outer_simdir, 'output%d.txt' % rep), 'w').write(stdoutput)

    ##############################
    # Set up the "smc" directory #
    ##############################
    infile  = os.path.join(outer_smcdir, '%s-smctree.conf' % setupmain.user)
    outfile = infile
    smc_mu = extinction_rate
    smc_lambda = speciation_rate
        
    if setupmain.user == "aam21005":
        setupsubst.substitutions({
            '__RNSEED__':    rnseed, 
            '__SUBSETS__':   subsets,
            '__MU__': smc_mu, 
            '__LAMBDA__':    smc_lambda,
            '__SMCNPARTICLES__': setupmain.smc_nparticles,
            '__SMCNGROUPS__': setupmain.smc_ngroups,
            '__SMCSAVEEVERY__': setupmain.smc_saveevery,
            '__SMCNTHREADS__': setupmain.smc_nthreads,
            }, infile, outfile)
    os.rename(outfile, os.path.join(outer_smcdir, 'smctree.conf'))
    
    ################################
    # Append to the "smc.sh" file #
    ################################
    smc_for_rep = 'cd %s\n%s\ncd -\n\n# __SMC__' % (inner_smcdir, setupmain.smc_path)
    infile = os.path.join(maindir, 'smc.sh')
    outfile = infile
    setupsubst.substitutions({
        '# __SMC__': smc_for_rep
        }, infile, outfile)
    
    ##################################
    # Append to the "rfsmc.nex" file #
    ##################################
    smcrf_for_rep = '''
    gettrees file = %s/sim.tre mode=3;
    gettrees file = %s/%s mode=7;
    deroot;
    treedist all / measure=rfSymDiff refTree=1 file=smcrf%d.txt;
    [__RFSMC__]''' % (inner_simdir,inner_smcdir,setupmain.smc_treefile,rep)
    infile = os.path.join(maindir, 'rfsmc.nex')
    outfile = infile
    setupsubst.substitutions({
        r'\[__RFSMC__\]': smcrf_for_rep
        }, infile, outfile)

    refinfof.close()
