import fst

# First load an FST that maps letters to words with unigram weights
#
# You can create this FST using letter2unigram.py like this:
# python letter2unigram.py CORPUS l2u.fst
# where CORPUS is the name of a text file

let2word = fst.load("l2u.fst")

# Then create a new FST that maps digits to letters,
# using the same symbol table
dig2let = fst.new(let2word)

dig2let.add_arc('0', '0', '2', 'a', 0)
dig2let.add_arc('0', '0', '2', 'b', 0)
dig2let.add_arc('0', '0', '2', 'c', 0)
dig2let.add_arc('0', '0', '3', 'd', 0)
dig2let.add_arc('0', '0', '3', 'e', 0)
dig2let.add_arc('0', '0', '3', 'f', 0)
dig2let.add_arc('0', '0', '4', 'g', 0)
dig2let.add_arc('0', '0', '4', 'h', 0)
dig2let.add_arc('0', '0', '4', 'i', 0)
dig2let.add_arc('0', '0', '5', 'j', 0)
dig2let.add_arc('0', '0', '5', 'k', 0)
dig2let.add_arc('0', '0', '5', 'l', 0)
dig2let.add_arc('0', '0', '6', 'm', 0)
dig2let.add_arc('0', '0', '6', 'n', 0)
dig2let.add_arc('0', '0', '6', 'o', 0)
dig2let.add_arc('0', '0', '7', 'p', 0)
dig2let.add_arc('0', '0', '7', 'q', 0)
dig2let.add_arc('0', '0', '7', 'r', 0)
dig2let.add_arc('0', '0', '7', 's', 0)
dig2let.add_arc('0', '0', '8', 't', 0)
dig2let.add_arc('0', '0', '8', 'u', 0)
dig2let.add_arc('0', '0', '8', 'v', 0)
dig2let.add_arc('0', '0', '9', 'w', 0)
dig2let.add_arc('0', '0', '9', 'x', 0)
dig2let.add_arc('0', '0', '9', 'y', 0)
dig2let.add_arc('0', '0', '9', 'z', 0)

dig2let.set_start('0')
dig2let.set_final('0')

# To create the letter to digit FST, we could do the same as above:

# let2dig.add_arc('0', '0', 'a', '2', 0)
# let2dig.add_arc('0', '0', 'b', '2', 0)
# let2dig.add_arc('0', '0', 'c', '2', 0)
# let2dig.add_arc('0', '0', 'd', '3', 0)
# ...
# let2dig.set_start('0')
# let2dig.set_final('0')

# Or we can instead use the invert() functionality in openfst.

# First create a new FST with the same symbol table as dig2let
let2dig = fst.new(dig2let)

# Now copy the openfst FST directly
let2dig.f = dig2let.f.copy()

# And invert it, which just swaps input/output symbols in
# each transition
let2dig.f.invert()

# Now we have three transducers:
# 1. Unigram language model
# 2. Digit to letter
# 3. Letter to digit

# We can encode a string into a sequence of digits

# To create an FST that encodes a string, we first get a
# list with each symbol
str = "mary saw the dog in the park with the telescope"
letters = list(str)

# Then use linearchain().
# The first argument is the list of symbols,
# the second argument is an optional FST to take the symbol
# table from, and the last argument is an optional list of
# list items to ignore.
infst = fst.linearchain(letters, let2dig, [' '])

# Now encode the input FST (letters) into digits
encfst = fst.compose(infst, let2dig)

print("Input string: ", encfst.get_in_string())
print()
print("Output string:", encfst.get_out_string())
print()
print("Now reconstructing input string from the output string...\n")

# Then go from digits back to letters
decfst = fst.compose(encfst, dig2let)

# The mapping is now one to many, so we can choose out
# strings based on unigram score

# Compose the decoded string FST with the unigram model FST
decscored = fst.compose(decfst, let2word)

# Now the paths in the decoded FST are scored, and we can see
# the best strings according to the model.
# Did we reconstruct the original string?
sp = fst.shortest_path_list(decscored, 10)
for path in sp:
    print("%.2f\t%s" % (path[0], path[2]))

