import fst
import math
import sys

# A dictionary to hold a frequency distribution
fd = {}

# The FST
f = fst.new()

# A token counter
token_count = 0

# Minimum count threshold for words
min_count = 5

# Open a text file and read it line by line
with open(sys.argv[1], 'r') as fp:
    for line in fp:

        # Get each token, separated by spaces
        toks = line.split()

        # Add the tokens to the dictionary
        for t in toks:
            token_count += 1
            if t in fd:
                fd[t] += 1
            else:
                fd[t] = 1

# Remove words that appeared fewer than five times
unks = [word for word, count in fd.items() if count < min_count]

# Put the unknown word in the dictionary, with count zero
fd['<unk>'] = 0

for word in unks:
    fd['<unk>'] += fd[word]
    fd.pop(word)

# Now build the FST
state = 1
for w in fd:

    # fd[w] divided by token_count is the relative frequency,
    # or unigram probability.
    #
    # The weight will be negative log unigram probability 
    weight = math.log(fd[w]/token_count) * -1
    f.add_arc(0, 0, w, None, weight)
    
f.set_start(0)
f.set_final(0)

f.f.arcsort()

f.save(sys.argv[2])
