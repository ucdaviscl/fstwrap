import fst
import math
import pickle
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
    letters = list(w)

    # Add each letter to a path in the FST
    zero = True
    for letter in letters:
        if zero:
            f.add_arc(0, state, letter, '<epsilon>', 0)
            zero = False
        else:
            f.add_arc(state-1, state, letter, '<epsilon>', 0)
            
        state += 1

    # Got to the end of the path, so go back to the start
    # and output the word
    f.add_arc(state-1, 0, '<epsilon>', w, weight)
    
f.add_arc('fail', 'fail', '0', None, weight)
f.add_arc('fail', 'fail', '1', None, weight)
f.add_arc('fail', 'fail', '2', None, weight)
f.add_arc('fail', 'fail', '3', None, weight)
f.add_arc('fail', 'fail', '4', None, weight)
f.add_arc('fail', 'fail', '5', None, weight)
f.add_arc('fail', 'fail', '6', None, weight)
f.add_arc('fail', 'fail', '7', None, weight)
f.add_arc('fail', 'fail', '8', None, weight)
f.add_arc('fail', 'fail', '9', None, weight)
    
f.set_start(0)
f.set_final(0)

f.f.arcsort()

f.save(sys.argv[2])
