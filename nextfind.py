#!/bin/python

from subprocess import *
import re
import sys

I3MSG = '/usr/bin/i3-msg';
DMENU = '/usr/bin/dmenu';

p1 = Popen([I3MSG, "-t", "get_tree"], stdout=PIPE)
i3input = str(p1.communicate()[0])
p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.

count = 0
current = -1
targets = dict()

#find all the named windows that have type 2 (actually a window I think)
#and create a dictionary so that the user to can search through
sections = re.split('"id":', i3input);
for idset in sections:
	results1 = re.search('([0-9]*).*focused":(false|true).*"geometry":{.*?"width":(?!0).*"name":"(.*?)"', idset)
	if results1 != None:
		if results1.group(2) == "true":
			current = int(results1.group(1))

		if targets.get(results1.group(3)) == None:
			targets[results1.group(3)] = []
		targets[results1.group(3)].append(results1.group(1))

#if there were no windows, provide no options
if len(targets) == 0:
	sys.exit(1)

#modify keys to indicate the number of matching windows
options = dict()
for key in targets:
	print(key)
	newkey = "(" + str(len(targets[key])) + ") " + key
	options[newkey] = targets[key]

#run dmenu to provide options
p1 = Popen([DMENU, '-i'], stdout=PIPE, stdin=PIPE)
concat = '\n'.join(options.keys())
i3input = p1.communicate(bytes(concat, 'UTF-8'))[0]
p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.

#get the choice
print(i3input)
print(i3input.decode('UTF-8'))
key = i3input.decode('UTF-8')[0:-1]
print(key)
print(options)
print(options[key])

#if the choice is a window type that has multiple values, then pick the next
#from the current, in order of id
numtargs = [int(val) for val in options[key]]
print(current)
print(numtargs)
if current in numtargs:
	numtargs.sort();
	pos = list.index(numtargs, current);
	ii = (pos + 1)%len(numtargs)
else:
	ii = 0

print([I3MSG, '[con_id="'+str(numtargs[ii])+'"] focus'])
p1 = Popen([I3MSG, '[con_id="'+str(numtargs[ii])+'"] focus'])