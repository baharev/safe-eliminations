# BSD 3-Clause License
# Copyright (c) 2017, University of Vienna
# All rights reserved.
# Author: Ali Baharev <ali.baharev@gmail.com>
# https://github.com/baharev/safe-eliminations
from __future__ import division, print_function
from collections import OrderedDict
import sympy as sp
import imp
from six import exec_ 

EQUATIONS = '''
    x  + y    + z - 2
         y**2 + z - 3
log(x) +      + z - 1.0
'''

VAR_BOUNDS = OrderedDict([('x', (-10.0, 10.0)), ('y', (-4, 4)), ('z', (-6, 6))])

VAR_ORDER = {name: i for i, name in enumerate(VAR_BOUNDS)}

def main():
    eqs = [sp.sympify(line) for line in EQUATIONS.splitlines() if line.strip()]
    n_eqs, n_vars = len(eqs), len(VAR_ORDER)
    print('The system of equations:')
    print('\n'.join(str(eq) for eq in eqs))
    print('Size: %d x %d' % (n_eqs, n_vars))
    solvability_pattern = []
    for eq in eqs:
        print('------------------------------------------------------------')
        print('Trying to solve: %s = 0 for each variable\n' % str(eq))
        variables = [v for v in eq.atoms(sp.Symbol) if not v.is_number]
        variables = sorted(variables, key=lambda v: VAR_ORDER[str(v)])
        print('Variables:', variables)
        print()
        var_names = [str(v) for v in variables]
        var_bounds = [(v, VAR_BOUNDS[str(v)]) for v in var_names]
        solutions = symbolic_sols(eq, variables, var_bounds)
        row = [' '] * n_vars
        for v in var_names:
            row[VAR_ORDER[v]] = 'S' if v in solutions else 'U'
        solvability_pattern.append(row)
    pretty_print_solvability_pattern(solvability_pattern, n_vars)
    print('Done!')

def pretty_print_solvability_pattern(solvability_pattern, n_vars):
    var_names = list(VAR_BOUNDS)
    print('============================================================')
    print('The equations were (left-hand side = 0, only left-hand side shown):')
    print(EQUATIONS)
    print('Variable bounds:\n')
    for name, (lb, ub) in VAR_BOUNDS.items():
        print('{} <= {} <= {}'.format(lb, name, ub))
    print()
    print('Solvability pattern')
    print('S: solvable')
    print('U: unsolvable/unsafe elimination given the variable bounds')
    print()
    indent = '  '
    print(indent, '  '.join(var_names))
    print(indent, '-'*(n_vars + 2*(n_vars-1)))
    for i, row in enumerate(solvability_pattern):
        print(i, ' |','  '.join(entry for entry in row), sep='')
    print()

#-------------------------------------------------------------------------------

def symbolic_sols(eq, variables, varname_bnds):
    #print(eq)
    solutions = { } 
    for v in variables:
        sol = get_solution(eq, v, varname_bnds)
        if sol:
            solutions[str(v)] = sol
    return solutions

def get_solution(eq, v, varname_bnds):
    try:
        sol = sp.solve(eq, v, rational=False)
    except NotImplementedError as nie:
        print('<<<\n', nie, '\n>>>', sep='')
        return
    if len(sol) != 1: # Either no solution or multiple solutions
        return
    # Unique and explicit solution
    expression = str(sol[0])
    print(v, '=', expression)
    safe = check_safety(expression, varname_bnds)
    print('Is safe?', safe)
    print()
    return str(v) + ' = ' + expression if safe else None

eval_code = '''
try:
    from sympy.mpmath import iv
except ImportError:
    from mpmath import iv

iv.dps = 15

def is_safe():
    {varnames} = {varbounds}
    try:
        res = {expression}
    except:
        return False # e.g. ComplexResult: logarithm of a negative number
    return res in iv.mpf([-10**15, 10**15])
'''

def check_safety(expression, varname_bnds):
    names, ivbounds = [ ], [ ]
    bound_template = 'iv.mpf(({l}, {u}))'
    NegInf, PosInf = float('-inf'), float('inf')
    for name, bounds in varname_bnds:
        names.append(name)
        lb = str(bounds[0]) if bounds[0] != NegInf else "'-inf'"
        ub = str(bounds[1]) if bounds[1] != PosInf else "'inf'"
        ivbounds.append(bound_template.format(l=lb, u=ub))
    expression = expression.replace('exp', 'iv.exp')
    expression = expression.replace('log', 'iv.log')    
    code = eval_code.format(varnames   = ', '.join(names),
                            varbounds  = ', '.join(ivbounds),
                            expression = expression)
    #print(code)
    m = import_code(code)
    return m.is_safe()

def import_code(code):
    module = imp.new_module('someFakeName')
    try:
        exec_(code, module.__dict__)
    except:
        print(code)
        raise
    return module

if __name__ == '__main__':
    main()
