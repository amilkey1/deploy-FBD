import sys, re, os, subprocess as sub

nreps = __NREPS__

print("min:")
for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'rep%d/smc/hpd.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?', stuff, re.M | re.S)
	min = m1.group(0)
	print("\t", min, " ,", end='')

print ("\n")
print ("\n")
print("max:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/smc/hpd.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m2 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?', stuff, re.M | re.S)
        max = m2.group(0)
        print("\t", max, " ,", end='')

print ("\n")
print ("\n")
print("true:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/smc/hpd.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m3 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?(\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?)', stuff, re.M | re.S)
        true = m3.group(3)
        print("\t", true, " ,", end='')

print ("\n")
print ("\n")
print("observed:")
for rep in range(nreps):
        rep_plus_one = rep + 1

        # Extract rank
        fn = 'rep%d/smc/hpd.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m4 = re.search(r'\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?(\t[-+]?([0-9]*\.)?[0-9]+([eE][-+]?[0-9]+)?)', stuff, re.M | re.S)
        observed = m4.group(5)
        print("\t", observed, " ,", end='')
