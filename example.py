# BSD 3-Clause License
# Copyright (c) 2017, University of Vienna
# All rights reserved.
# Author: Ali Baharev <ali.baharev@gmail.com>
# https://github.com/baharev/safe-eliminations
from __future__ import division, print_function
from sympy import sympify, Symbol
from solvable import find_safe_eliminations


def main():
    # Input data of our example:
    equations = '''
        x  + y    + z - 2
             y**2 + z - 3
    log(x) +      + z - 1.0
    '''
    name_to_bounds = {'x': (-10.0, 10.0), 'y': (-4, 4), 'z': (-6, 6)}
    name_to_index  = {'x': 0, 'y': 1, 'z': 2}
    eqs = [sympify(line) for line in equations.splitlines() if line.strip()]
    #---------------------------------------------------------------------------
    # Show the input:
    print('The system of equations (only the left hand sides):')
    print('\n'.join(str(eq) for eq in eqs))
    print()
    print('Variable bounds:')
    for name in sorted(name_to_bounds):
        lb, ub = name_to_bounds[name]
        print(lb, '<=', name, '<=', ub)
    print()
    print('Size:', len(eqs), 'x', len(name_to_index))
    # Do the actual work:
    safe_eliminations = find_safe_eliminations(eqs, name_to_bounds)
    # Show what it did:
    for eq, solutions in zip(eqs, safe_eliminations):
        variables = [v for v in eq.atoms(Symbol) if not v.is_number]
        eq = str(eq)
        variables = [str(v) for v in variables]
        variables = sorted(variables, key=lambda v: name_to_index[v])
        print('---------------------------------------------------------------')
        print('Examining each variable in', eq, '= 0 for elimination')
        print('Variables:', ', '.join(variables))
        for v in variables:
            print()
            if v in solutions:
                print('Variable', v, 'can be safely eliminated:')
                print(v, '=', str(solutions[v]))
            else:
                print('The algorithm failed to prove that it is safe to eliminate')
                print(v, 'from', eq ,'= 0')

if __name__ == '__main__':
    main()
