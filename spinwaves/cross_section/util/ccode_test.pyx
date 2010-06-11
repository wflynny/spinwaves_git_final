# ccode_test.pyx
# cython: profile = True

import cython
import sympy as sp

def evaluate_c(expr, var, double val):
    print var
    var = val
    print var
    print expr
    return expr

def sample_run():
    x = sp.Symbol('x')
    e = sp.sqrt(x)
    f = sp.ccode(e)
    return evaluate_c(f,x,4)
    
