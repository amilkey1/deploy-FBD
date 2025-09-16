import subprocess as sub
import sys,os,re,math,shutil
import setupsubst

# Specify NetID of user (this is for specifying home directories and choosing among template files)
user = 'aam21005'

# Specify local = True if testing on your local laptop; if running on cluster set local = False
local = True

# This directory will be created and will contain the master slurm scripts as well
# as a subdirectory for every simulation replicate
maindir = 'g'

# Specify the master pseudorandom number seed
master_seed = 1

# Specify whether grid should be mu vs lambda - always set to true
mu_vs_lambda = True

#########
# Paths #
#########

if user == 'aam21005':
    if local:
        simulator_path = 'fbd'
        smc_path       = 'fbd'
    else:
        simulator_path = 'fbd'
        smc_path       = 'fbd'

#######################
# Simulation settings #
#######################

# Whether to use FASTA or NEXUS format for individual locus-specific data files
useFASTA = True

# No. points along the x and y axes
ngridpoints = 3

# If ngridpoints > 1, this option is ignored and nreps is
# instead set to ngridpoints^2
nreps = 1

# number of loci varies among simulations
#nloci           = 10
min_n_loci = 10
max_n_loci = 10

min_sites_per_locus = 1000
max_sites_per_locus = 1000

# Variance of lognormal distribution governing variation
# among rates on each edge of a gene tree. The mean rate
# is 1.0 because these are relative rates.
min_edge_rate_variance = 0.0
max_edge_rate_variance = 0.0

# Shape of Gamma distribution determining relative rates among loci
# Mean must equal 1, so scale=1/shape and variance = shape*scale^2 = 1/shape
subset_relrate_shape = 10000.0

# Shape of Gamma distribution determining relative rates among sites
# within loci. Mean must equal 1, so scale = 1/shape and variance = shape*scale^2 = 1/shape
min_asrv_shape = 10000.0
max_asrv_shape = 10000.0

# Occupancy is the probability that a particular taxon will
# be included for a particular gene. 1.0 means there will be
# data for all taxa in all genes. 0.9 means that, on average,
# 10% of taxa will have all missing data for any given locus
min_occupancy = 1.0
max_occupancy = 1.0

# Compositional heterogeneity is determined by a Dirichlet(a,a,a,a)
# distribution for any given locus. For example, setting 
# comphet = 1000 will ensure that piA, piC, piG, piT are all
# very nearly 0.25 for a locus, while comphet = 1 results in
# a completely unpredictable set of equilibrium base frequencies
# for a locus.
min_comphet = 10000
max_comphet = 10000

species            = ['A', 'B', 'C', 'D', 'E']
indivs_for_species = [ 2,   2,   2,   2,   2]

if mu_vs_lambda:
    
    mu_min = 1.0
    mu_max = 100.0
    
    lambda_min = 1.0
    lambda_max = 100.0
    
################
# SMC settings #
################

# Determines values of theta and lambda provided to BEAST and SMC
# If True, use SVD-qage estimates of theta and lambda
# If False, use true theta and lambda
smc_use_svdq_estimates = False 

smc_nparticles        = 1000
if user == 'aam21005' or user == 'jjc23002':
    smc_saveevery		  = 1
    smc_nthreads		  = 3
    smc_ngroups			  = 3
    smc_treefile   = 'trees.trees'
else:
    assert False, 'user must be aam21005'

###########################################
# Calculated from settings provided above #
###########################################

if ngridpoints > 1:
    nreps = ngridpoints*ngridpoints
    
subset_relrate_scale = 1.0/subset_relrate_shape

def run(maindir, nreps):
    print('  setting up main directory')
                
    ###########################
    # Set up SMC slurm script #
    ###########################
    smc_slurm_path = os.path.join(maindir, 'smc.slurm')
    setupsubst.substitutions({
        '__SMC_PATH__': smc_path,
        '__NJOBS__': nreps,
        '__MAINDIR__': maindir
        }, smc_slurm_path, smc_slurm_path)
        
    ###########################
    # Set up rfsmc.nex script #
    ###########################
    rfsmc_path = os.path.join(maindir, 'rfsmc.nex')
    smc_samplesize = 0
    if user == "aam21005":
        smc_samplesize = smc_nparticles * smc_ngroups / smc_saveevery
    smc_samplesize = int(smc_samplesize)
    setupsubst.substitutions({
        '__MAXTREES__': smc_samplesize + 1
        }, rfsmc_path, rfsmc_path)
        
    #########################################
    # Set up ruv.py script #
    #########################################
    ruv_path = os.path.join(maindir, 'ruv.py')
    setupsubst.substitutions({
        '__NREPS__': nreps,
        }, ruv_path, ruv_path)
