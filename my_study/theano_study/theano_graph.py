'''
Created on Jan 14, 2016

@author: nlp
'''
import pydot
import theano
import theano.tensor


a = theano.tensor.vector("a")  # declare symbolic variable
b = a + a ** 10  # build symbolic expression
f = theano.function([a], b)  # compile function
print f([0, 1, 2])  # prints `array([0,2,1026])`

# theano.printing.pydotprint(b, outfile="symbolic_graph_unopt.png", var_with_name_simple=True)  
theano.printing.pydotprint(f, outfile="symbolic_graph_opt.png", var_with_name_simple=True)  
