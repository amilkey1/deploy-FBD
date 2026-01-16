import sys, re, os, subprocess as sub

nreps = __NREPS__

print("true_values:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/sim/nodes_with_fossil_calibration_ages.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        print("\t", stuff, ",", end='')

print("95%_hpd_min:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/smc/nodes_with_fossil_calibration_ages.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m2 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?', stuff, re.M | re.S)
        max = m2.group(0)
        print("\t", max, " ,", end='')

print ("\n")
print ("\n")
print("95%_hpd_max:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/smc/nodes_with_fossil_calibration_ages.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m3 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?(\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?)', stuff, re.M | re.S)
        true = m3.group(3)
        print("\t", true, " ,", end='')

print ("\n")
print ("\n")
print("observed_mean:")
for rep in range(nreps):
        rep_plus_one = rep + 1

        # Extract rank
        fn = 'rep%d/smc/nodes_with_fossil_calibration_ages.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m4 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?(\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?)', stuff, re.M | re.S)
        observed = m4.group(5)
        print("\t", observed, " ,", end='')