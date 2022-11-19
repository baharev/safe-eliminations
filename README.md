# Identifying numerically safe eliminations automatically

The background is discussed in *2. Identifying feasible assignments* of

[Ordering matrices to bordered lower triangular form with minimal border width](https://baharev.info/publications/baharev_tearing_exact_algorithm.pdf).

The code here is derived from:

https://github.com/baharev/sdopt-tearing/blob/master/sympy_tree.py

However, `sympy_tree.py` is concerned with binary expression trees coming 
from [Modelica](https://en.wikipedia.org/wiki/Modelica#Examples) and 
generating output for 
[AMPL](https://en.wikipedia.org/wiki/AMPL#A_sample_model).
The `solvable.py` is only concerned with expression trees coming from, and 
going to [SymPy](http://docs.sympy.org/latest/tutorial/manipulation.html).  
**The caveats mentioned in the last two paragraphs of 
*2.2. Identifying numerically troublesome assignments* in 
[Ordering matrices to bordered lower triangular form with minimal border width](https://baharev.info/publications/baharev_tearing_exact_algorithm.pdf) 
do apply!**

Of course, the long-term goal is to merge the code back into 
[sdopt-tearing](https://github.com/baharev/sdopt-tearing).
