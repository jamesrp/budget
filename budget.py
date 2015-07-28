import csv
import sys
import collections

csvname = sys.argv[1]
# We expect csv to have header fields:
# Date, No, Description, Debit, Credit
# This is how my bank does it.
# We only care about Date, Description, Debit.
date_index = 0
description_index = 2
debit_index = 3
indices = [date_index, description_index, debit_index]


lines = []
with open(csvname, 'rb') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in csvreader:
        lines.append([row[x] for x in indices])

# Now to group by description. Note that indices are now 0, 1, 2.
# We will also remove the first row (header row)
lines = lines[1:]

# Convert entries to floats and negate them to get positive numbers
lines = [[a, b, -float(c)] for a,b,c in lines]

# Some heuristic grouping
def is_grocery(desc):
    names = ["PCC", "SAFEWAY", "WHOLEFDS", "SCHUH", "COWEN PARK", "SWANSONS",
        "HAYTON", "TALL GRASS", "HERKIMER", "NNT COWEN", "FRED MEYER"]
    return any(desc.find(x) > -1 for x in names)

def to_grocery(desc):
    if is_grocery(desc):
        return "GROCERIES"
    return desc

def trim(desc):
    extras = ["External Withdrawal - ", "POS Withdrawal - "]
    for e in extras:
        s = desc.split(e)
        if len(s) > 1:
            desc = s[1]
    return desc

def to_amazon(desc):
    if desc.lower().find("amazon") == -1:
        return desc
    return "AMAZON"

def to_cat(desc):
    if desc.find("PETAPOLUZA") != -1 or desc.find("MUD BAY") != -1:
        return "CAT"
    return desc

def should_keep(desc):
    return desc.find("Withdrawal - Online Banking Transfer") == -1 \
        and desc.find("SIMPLE") == -1

lines = [[date, trim(to_cat(to_amazon(to_grocery(desc)))), debit] for date, desc, debit in lines
    if should_keep(desc)]

bydesc = collections.defaultdict(float)
for row in lines:
    bydesc[row[1]] += row[2]

descs = bydesc.keys()
descs.sort(key = lambda k: bydesc[k])
for d in descs:
    print bydesc[d], d

total = sum(row[2] for row in lines)
print "Total output\n", total

# Print the 80% of expenses
target = 0.8 * total
accum = 0
for d in reversed(descs):
    accum += bydesc[d]
    print bydesc[d], d
    if accum >= target:
        break

