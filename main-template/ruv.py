import sys, re, os, subprocess as sub

nreps = __NREPS__
for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'rep%d/smc/rank_first_split.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m = re.search(r'rank: (?P<rank>[.0-9]+)', stuff, re.M | re.S)
	rank = float(m.group('rank'))
	print(rank, ",", end='')
