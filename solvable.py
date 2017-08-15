# Copyright (C) 2017 University of Vienna
# All rights reserved.
# BSD license.
# Author: Ali Baharev <ali.baharev@gmail.com>
from __future__ import division, print_function
from collections import OrderedDict
import sympy as sp
import imp
from six import exec_
import logging


def main(eqs, var, variable_bounds):

    n_eqs, n_vars = len(eqs), len(var)
    logging.debug('The system of equations:')
    logging.debug('\n'.join(str(eq) for eq in eqs))
    logging.debug('Size: %d x %d' % (n_eqs, n_vars))
    solvability_pattern = []
    for eq in eqs:
        logging.debug('------------------------------------------------------------')
        logging.debug('Trying to solve: %s = 0 for each variable\n' % str(eq))
        variables = [v for v in eq.atoms(sp.Symbol) if not v.is_number]
        variables = sorted(variables, key=lambda v: var[str(v)])
        logging.debug('Variables: {}\n'.format(variables))

        var_names = [str(v) for v in variables]
        var_bounds = [(v, variable_bounds[str(v)]) for v in var_names]
        solutions = symbolic_sols(eq, variables, var_bounds)
        row = [' '] * n_vars
        for v in var_names:
            row[var[v]] = 'S' if v in solutions else 'U'
        solvability_pattern.append(row)

    return solvability_pattern, n_vars


def pretty_print_solvability_pattern(solvability_pattern, n_vars, variable_bounds, eqs):
    var_names = list(variable_bounds)
    logging.debug('============================================================')
    logging.debug('The equations were (left-hand side = 0, only left-hand side shown):')
    logging.debug(eqs)
    logging.debug('Variable bounds:\n')
    for name, (lb, ub) in variable_bounds.items():
        logging.debug('{} <= {} <= {}'.format(lb, name, ub))

    logging.debug('\nSolvability pattern')
    logging.debug('S: solvable')
    logging.debug('U: unsolvable/unsafe elimination given the variable boundsn\n')

    indent = '   '
    logging.debug('{}{}'.format(indent, '  '.join(var_names)))
    logging.debug('{}{}'.format(indent, '-'*(n_vars + 2*(n_vars-1))))
    for i, row in enumerate(solvability_pattern):
        logging.debug('{}{}{}'.format(i, ' |', '  '.join(entry for entry in row)))

# -------------------------------------------------------------------------------


def symbolic_sols(eq, variables, varname_bnds):
    # print(eq)
    solutions = {}
    for v in variables:
        sol = get_solution(eq, v, varname_bnds)
        if sol:
            solutions[str(v)] = sol
    return solutions


def get_solution(eq, v, varname_bnds):
    try:
        sol = sp.solve(eq, v, rational=False)
    except NotImplementedError as nie:
        logging.error('{}{}{}'.format('<<<\n', nie, '\n>>>'))
        return
    if len(sol) != 1:  # Either no solution or multiple solutions
        return
    # Unique and explicit solution
    expression = str(sol[0])
    logging.debug('{}{}{}'.format(v, '=', expression))
    safe = check_safety(expression, varname_bnds)
    logging.debug('{}{}\n'.format('Is safe?', safe))
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
    names, ivbounds = [], []
    bound_template = 'iv.mpf(({l}, {u}))'
    NegInf, PosInf = float('-inf'), float('inf')
    for name, bounds in varname_bnds:
        names.append(name)
        lb = str(bounds[0]) if bounds[0] != NegInf else "'-inf'"
        ub = str(bounds[1]) if bounds[1] != PosInf else "'inf'"
        ivbounds.append(bound_template.format(l=lb, u=ub))
    expression = expression.replace('exp', 'iv.exp')
    expression = expression.replace('log', 'iv.log')    
    code = eval_code.format(varnames=', '.join(names),
                            varbounds=', '.join(ivbounds),
                            expression=expression)
    # print(code)
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
    logging.basicConfig(level=logging.DEBUG)

    EQUATIONS = '''
        x  + y    + z - 2
             y**2 + z - 3
    log(x) +      + z - 1.0
    '''

    VAR_BOUNDS = OrderedDict([('x', (-10.0, 10.0)), ('y', (-4, 4)), ('z', (-6, 6))])

    VAR_ORDER = {name: i for i, name in enumerate(VAR_BOUNDS)}

    EQS = [sp.sympify(line) for line in EQUATIONS.splitlines() if line.strip()]

    solvability_pattern_list, number_of_vars = main(EQS, VAR_ORDER, VAR_BOUNDS)

    pretty_print_solvability_pattern(solvability_pattern_list, number_of_vars, VAR_BOUNDS, EQS)
    logging.debug('\nDone!')
