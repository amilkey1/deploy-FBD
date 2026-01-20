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
master_seed = 123

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
        simulator_path = 'fbd-smc'
        smc_path       = 'fbd-smc'

#######################
# Simulation settings #
#######################

# Whether to use FASTA or NEXUS format for individual locus-specific data files
useFASTA = True

# No. points along the x and y axes
ngridpoints = 10

# If ngridpoints > 1, this option is ignored and nreps is
# instead set to ngridpoints^2
nreps = 1

# number of loci varies among simulations
#nloci           = 10
min_n_loci = 1
max_n_loci = 1

min_sites_per_locus = 1000
max_sites_per_locus = 1000

# Shape of Gamma distribution determining relative rates among loci
# Mean must equal 1, so scale=1/shape and variance = shape*scale^2 = 1/shape
subset_relrate_shape = 10000.0

species            = ['A', 'B', 'C', 'D', 'E']

mu_min = 0.2
mu_max = 0.2


lambda_min = 1.0
lambda_max = 1.0

################
# SMC settings #
################

smc_nparticles        = 10000
if user == 'aam21005':
    smc_saveevery		  = 100
    smc_nthreads		  = 3
    smc_ngroups			  = 5
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
        '__NJOBS__': nreps
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

    #########################################
    # Set up coverage.py script #
    #########################################
    coverage_path = os.path.join(maindir, 'coverage.py')
    setupsubst.substitutions({
        '__NREPS__': nreps,
        }, coverage_path, coverage_path)
