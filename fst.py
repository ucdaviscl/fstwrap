# A simple wrapper for the OpenFST python wrapper.

import pywrapfst as openfst

class fst:

    # We can optionally initialize the fst with another fst,
    # just to get the same symbol table
    def __init__(self, symfst=None):

        # syms map integer IDs to string symbols,
        # and symids map string symbols to integer IDs

        # We start by adding the <epsilon> symbol
        # with ID 0
        self.syms = ['<epsilon>']
        self.symids = {'<epsilon>':0}

        # Keep track of states in the same way
        self.states = []
        self.stateids = {}

        # Create a new FST using OpenFST
        self.f = openfst.Fst()

        # Optionally initialize the symbol table using
        # the symbol table from another FST
        if symfst != None:
            self.syms = symfst.syms
            self.symids = symfst.symids

    # Given a state name, return the ID.
    # If the name doesn't exist, create a new state
    # and return its ID.
    def get_stateid(self, state):
        if state in self.stateids:
            return self.stateids[state]
        s = self.f.add_state()
        self.stateids[state] = s
        self.states.append(state)
        return s

    # Given a symbol, return the ID.
    # If the symbol doesn't exist, add it to the symbol table
    # and return its ID.
    def get_symid(self, symstr):
       if symstr in self.symids:
           return self.symids[symstr]
       symid = len(self.syms)
       self.symids[symstr] = symid
       self.syms.append(symstr)
       return symid

   # Set the start state for the FST
    def set_start(self, state):
        if state not in self.stateids:
            return False
        self.f.set_start(self.stateids[state])
        return True

    # Make a state a final state
    def set_final(self, state):
        if state not in self.stateids:
            return False
        self.f.set_final(self.stateids[state])
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
                state1 = self.states[stateid]
                isym = self.syms[arc.ilabel]
                osym = self.syms[arc.olabel]
                weight = float(arc.weight)
                state2 = self.states[arc.nextstate]

                startstr = '-'
                if self.f.start() == stateid:
                    startstr = '+'
                    
                #print(startstr, state1, '[', stateid, ']', \
                #      state2, '[', arc.nextstate, ']', arc.ilabel, \
                #      isym, arc.olabel, osym, weight, sep=' ')

                print(startstr, state1, state2, isym, osym, weight, sep='\t')


# Create a new FST
def new(f=None):
    g = fst(f)
    return g

# FST Composition
def compose(f, g):
    # First create a new FST with the same symbol table as f
    c = fst(f)

    # Use OpenFST composition
    c.f = openfst.compose(f.f, g.f)

    # Keep track of the states
    for stateid in c.f.states():
        c.states.append(str(stateid))
        c.stateids[str(stateid)] = stateid

    return c

# Shortest Path
# f is the FST and n is the number of shortest paths
def shortest_path(f, n=1):
    # create the FST that will encode the shortest paths,
    # with the same symbol table as f
    s = fst(f)

    # OpenFST shortest path
    s.f = openfst.shortestpath(f.f, nshortest=n)

    # Keep track of the states
    for stateid in s.f.states():
        s.states.append(str(stateid))
        s.stateids[str(stateid)] = stateid

    return s

# Put n shortest paths from FST f in a list
# Return a list of tuples (input_string, output_string, weight)
def shortest_path_list(f, n=1):
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
            in_sym = s.syms[arc.ilabel]
            if in_sym != '<epsilon>':
                istr += in_sym + " "

            # Add the output symbol
            out_sym = s.syms[arc.olabel]
            if out_sym != '<epsilon>':
                ostr += out_sym + " "

            # Put the next state on the stack
            state_stack.append(arc.nextstate)

    return sorted(sp)

# A sample driver 
def main():

    # Create an FST
    f = fst()
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
    g = fst(f)
    g.add_arc('zero', 'one', 'ojeda', None, 1)
    g.add_arc('one', 'two', 'said', None, 1)
    g.add_arc('two', 'three', 'that', None, 1)
    g.add_arc('three', 'four', 'language', None, 1)
    g.add_arc('four', 'five', 'is', None, 1)
    g.add_arc('five', 'six', 'infinite', None, 1)
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
    
