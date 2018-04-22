# A simple wrapper for the OpenFST python wrapper.

import pickle
import pywrapfst as openfst

class fst:

    # We can optionally initialize the fst with another fst,
    # just to get the same symbol table
    def __init__(self, symtab=None, symfile=None):

        if symtab == None:
            self.symtab = openfst.SymbolTable()
            self.symtab.add_symbol('<epsilon>')
            
            if symfile != None:
                self.symtab.read_text(symfile)
        else:
            self.symtab = symtab
            if self.symtab.find('<epsilon>') == -1:
                self.symtab.add_symbol('<epsilon>')
            
        # Keep track of states
        self.statetab = openfst.SymbolTable()

        # Create a new FST using OpenFST
        self.f = openfst.Fst()

    # If the name doesn't exist, create a new state
    # and return its ID.
    def get_stateid(self, state):
        statestr = str(state)
        id = self.statetab.find(statestr)
        if id == -1:
            id = self.statetab.add_symbol(statestr)
            sid = self.f.add_state()
            if id != sid:
                print("ERROR: state ID mismatch")
        return id

    # Given a symbol, return the ID.
    # If the symbol doesn't exist, add it to the symbol table
    # and return its ID.
    def get_symid(self, sym):
        symstr = str(sym)
        id = self.symtab.find(symstr)
        if id == -1:
            id = self.symtab.add_symbol(symstr)
        return id

   # Set the start state for the FST
    def set_start(self, state):
        if str(state) not in self.statetab:
            return False
        self.f.set_start(self.get_stateid(state))
        return True

    # Make a state a final state
    def set_final(self, state):
        if str(state) not in self.statetab:
            return False
        self.f.set_final(self.get_stateid(state))
        return True

    # Add an arc to the FST
    def add_arc(self, state1, state2, isym, osym, weight):

        # First get the state IDs
        sid1 = self.get_stateid(state1)
        sid2 = self.get_stateid(state2)

        # If we don't have an output symbol, just use
        # the same as the input symbol
        if osym == None:
            osym = isym

        # Get the IDs for the input and output symbols
        isymid = self.get_symid(isym)
        osymid = self.get_symid(osym)

        # Add the arc using OpenFST
        arc = openfst.Arc(isymid, osymid, weight, sid2)
        self.f.add_arc(sid1, arc)

        return True

    # Print the FST using a text format
    def print(self):
        # Go through all the states
        for stateid in self.f.states():
            # Go through all the arcs for the current state
            for arc in self.f.arcs(stateid):
                state1 = self.statetab.find(stateid).decode()
                isym = self.symtab.find(arc.ilabel).decode()
                osym = self.symtab.find(arc.olabel).decode()
                weight = float(arc.weight)
                state2 = self.statetab.find(arc.nextstate).decode()

                startstr = '-'
                if self.f.start() == stateid:
                    startstr = '+'
                    
                #print(startstr, state1, '[', stateid, ']', \
                #      state2, '[', arc.nextstate, ']', arc.ilabel, \
                #      isym, arc.olabel, osym, weight, sep=' ')

                print(startstr, state1, state2, isym, osym, weight, sep='\t')

    # Save the FST
    def save(self, fname):
        with open(fname, 'wb') as fp:
            pickle.dump(self, fp)

    # Get an input string
    def get_in_string(self, n=1, sep=''):
        str = ''
        sp = shortest_path_list(self, n)
        i = 0
        for path in sp:
            for sym in path[1]:
                str += sym
        return str
                
    # Get an output string
    def get_out_string(self, n=1, sep=''):
        str = ''
        sp = shortest_path_list(self, n, '')
        i = 0
        for path in sp:
            for sym in path[2]:
                str += sym
        return str


# Load an FST
def load(fname):
    newfst = None
    
    with open(fname, 'rb') as fp:
        newfst = pickle.load(fp)

    return newfst

# Create a new FST
def new(f=None):
    g = fst(f)
    return g

# Create a linear chain FST from a list
def linearchain(inlist, fstsym=None, exclude=[]):
    state = 0
    f = fst(fstsym)
    state = 0
    for sym in inlist:
        if sym in exclude:
            continue
        f.add_arc(state, state+1, sym, None, 0)
        state += 1
    f.set_start(0)
    f.set_final(state)
    
    return f

# FST Composition
def compose(f, g):
    # First create a new FST with the same symbol table as f
    c = fst(f.symtab)

    # Use OpenFST composition
    c.f = openfst.compose(f.f, g.f)

    # Keep track of the states
    for stateid in c.f.states():
        c.statetab.add_symbol(str(stateid))

    return c

# Shortest Path
# f is the FST and n is the number of shortest paths
def shortest_path(f, n=1):
    # create the FST that will encode the shortest paths,
    # with the same symbol table as f
    s = fst(f.symtab)

    # OpenFST shortest path
    s.f = openfst.shortestpath(f.f, nshortest=n)

    # Keep track of the states
    for stateid in s.f.states():
        s.statetab.add_symbol(str(stateid))

    return s

# Put n shortest paths from FST f in a list
# Return a list of tuples (input_string, output_string, weight)
def shortest_path_list(f, n=1, sep=" "):
    # The list of shortest paths
    sp = []

    # Get the FST that encodes the shortest paths
    s = shortest_path(f, n)
    
    # keep a stack of states
    state_stack = []

    # start at the start state
    state_stack.append(s.f.start())

    # current strings
    istr = ""
    ostr = ""
    weight = 0
    
    # keep going while there are states on the stack
    while len(state_stack) > 0:

        # take the next state to visit from the stack
        currst = state_stack.pop()

        # if it's a final state, print EOL
        #print(currst) #, s.states[currst])
        if float(s.f.final(currst)) == 0:
            sp.append((weight, istr, ostr))
            istr = ""
            ostr = ""
            weight = 0
            
        # Go through the arcs from the current state
        for arc in s.f.arcs(currst):

            # Add the weight
            weight += float(arc.weight)
            
            # Add the input symbol
            in_sym = s.symtab.find(arc.ilabel).decode()
            if in_sym != '<epsilon>':
                istr += in_sym + sep

            # Add the output symbol
            out_sym = s.symtab.find(arc.olabel).decode()
            if out_sym != '<epsilon>':
                ostr += out_sym + sep

            # Put the next state on the stack
            state_stack.append(arc.nextstate)

    return sorted(sp)

# A sample driver 
def main():

    sym = openfst.SymbolTable()
    
    # Create an FST
    f = fst(sym)
    f.add_arc('zero', 'one', 'ojeda', 'Ojeda', 3)
    f.add_arc('zero', 'one', 'ojeda', 'Prof_Ojeda', 2)
    f.add_arc('one', 'two', 'said', 'says', 1)
    f.add_arc('one', 'three', 'said', 'says', 1)
    f.add_arc('two', 'three', 'that', '<epsilon>', 1)
    f.add_arc('three', 'four', 'language', 'space', 1)
    f.add_arc('four', 'five', 'is', 'may_be', 1)
    f.add_arc('five', 'six', 'infinite', 'finite', 1)
    f.add_arc('five', 'six', 'infinite', 'infinite!', 2)
    f.set_start('zero')
    f.set_final('six')

    # Print the FST
    f.print()

    print()

    # Create another FST
    g = fst(sym)
    g.add_arc('zero', 'one', 'ojeda', None, 1)
    g.add_arc('one', 'two', 'said', None, 1)
    g.add_arc('two', 'three', 'that', None, 1)
    g.add_arc('three', 'four', 'language', None, 1)
    g.add_arc('four', 'five', 'is', None, 1)
    g.add_arc('five', 'six', 'infinite', None, 1)
    g.add_arc('five', 'six', 'abc', None, 1)
    g.set_start('zero')
    g.set_final('six')

    # Print the second FST
    g.print()

    print()

    # Compose and print the result
    c = compose(g, f)
    c.print()

    print()

    # Get the shortest path from the result of
    # the composition, and print the FST
    d = shortest_path(c)
    d.print()

    print()

    # Get a list of shorest paths from c
    sp = shortest_path_list(c, 10)

    for path in sp:
        print(path[0], path[2])

    print()
    
if __name__ == '__main__':
    main()
    
