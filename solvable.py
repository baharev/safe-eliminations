# BSD 3-Clause License
# Copyright (c) 2017, University of Vienna
# All rights reserved.
# Author: Ali Baharev <ali.baharev@gmail.com>
# https://github.com/baharev/safe-eliminations
from __future__ import division, print_function
import imp
from sys import stderr
from six import exec_
from sympy import solve, Symbol

__all__ = ['find_safe_eliminations']

def find_safe_eliminations(eqs, name_to_bounds, symbol_to_key=str):
    # eqs: iterable of SymPy expression trees, each tree represents the left
    #     hand side of an equation of form f(x) = 0.
    # name_to_bounds: either a dict or a function that maps a variable name to 
    #     the tuple of its lower bound and upper bounds. The variable names must
    #     be valid Python variable names, and must not clash with names of  
    #     mathematical functions such as exp or log.
    # symbol_to_key: a function that maps the SymPy Symbol (atom) of the 
    #     variables to the corresponding key in the returned dict. By default, 
    #     the variable names will be used as keys. If you want the indices 
    #     of the variables as keys, try something along these lines:
    #     `lambda v: name_to_index[str(v)]` where name_to_index maps a variable
    #     name to its desired index. 
    # Returns: The list of dictionaries of the safe eliminations, one dictionary
    #     per equation, in the order of eqs. The keys of the returned dicts are 
    #     determined by the symbol_to_key function (the keys will be the 
    #     variable names by default). The values in the dicts are the SymPy 
    #     expression trees: the safe eliminations when the equation is solved 
    #     for the variable corresponding to the key.
    # Warning: The algorithm is conservative in the sense that it only considers
    #     an elimination to be safe if it can prove it. If it fails to prove it,
    #     it considers it as unsafe, even if the elimination is safe in reality.
    #     The variables are assumed to have sane lower and upper bounds (10^100
    #     is not a sane variable bound). Although the algorithm tolerates 
    #     missing bounds, insane bounds, and even +infinity and -infinity as 
    #     bound, it is more likely that it will consider eliminations involving 
    #     such variables unsafe.
    #
    # See also the example.py.            
    return [safe_sols(eq, name_to_bounds, symbol_to_key) for eq in eqs]

def safe_sols(eq, name_to_bounds, symbol_to_key=str):
    solutions = {}
    variables = [v for v in eq.atoms(Symbol) if not v.is_number]
    names = [str(v) for v in variables]
    if hasattr(name_to_bounds, '__getitem__'):
        name_to_bounds = name_to_bounds.__getitem__
    bounds = [name_to_bounds(name) for name in names]
    assert all(b is not None for b in bounds) # A variable not in name_to_bounds?
    for v in variables:
        sol = get_safe_solution(eq, v, names, bounds)
        if sol is not None:
            solutions[symbol_to_key(v)] = sol
    return solutions

def get_safe_solution(eq, v, names, bounds):
    try:
        sol = solve(eq, v, rational=False)
    except NotImplementedError:
        # We treat it as "unsafe" to be on the safe side, altough it might be 
        # too conservative
        return
    if len(sol) != 1:  # Either no solution or multiple solutions
        return
    # Unique and explicit solution
    expression = sol[0]
    safe = is_safe_elimination(expression, names, bounds)
    return expression if safe else None

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

def is_safe_elimination(expression, names, bounds):
    bound_template = 'iv.mpf(({l}, {u}))'
    NegInf, PosInf = float('-inf'), float('inf')
    ivbounds = []
    for lb, ub in bounds:
        lb = str(lb) if lb != NegInf else "'-inf'"
        ub = str(ub) if ub != PosInf else "'inf'"
        ivbounds.append(bound_template.format(l=lb, u=ub))
    expression = str(expression)
    expression = expression.replace('exp', 'iv.exp')
    expression = expression.replace('log', 'iv.log')    
    code = eval_code.format(varnames=', '.join(names),
                            varbounds=', '.join(ivbounds),
                            expression=expression)
    module = imp.new_module('someFakeName')
    try:
        exec_(code, module.__dict__)
        return module.is_safe()
    except:
        warning('Please report this issue on GitHub! The problematic code was:')
        warning(code)
        raise

def warning(*args):
    print(*args, file=stderr)
