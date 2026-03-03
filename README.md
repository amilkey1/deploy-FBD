These scripts set up simulations for SMCTree (https://github.com/amilkey1/SMCtree/) program that performs divergence time estimation using sequential Monte Carlo.\

To run, change settings in `setup/setupmain.py` directory.\
Add simulated fossil settings (fossils and taxsets) in `rep-template/sim/'.conf` file.\
Add SMC fossil settings (fossils and taxsets) in `rep-template/smc/*.conf` file. Add RUV and coverage settings in this file as well.\

Set up the simulations:\
`python3 deploy.py`\
Run SMC analyses:\
`sbatch smc.slurm`\

Summarize output:\
`python3 ruv.py` to get ranks for validation.\
`python3 coverage.py` to get coverage intervals for validation.\
`python3 node-calibration.py` to extract information from output files 'nodes_with_fossil_calibration_ages.txt'. These files contain fossil number, 95% HPD intervals for sampled fossil dates, and observed means of sampled fossil dates. \
`plot-validation-template.Rmd` provides a template for visualizing validation output.\
