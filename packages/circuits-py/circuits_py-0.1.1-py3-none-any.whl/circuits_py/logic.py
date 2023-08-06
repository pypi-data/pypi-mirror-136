"""
logic gates which take int(1 or 0) or bool(True or False) arg/s
and return the output as a bool, not meant to be used directly

parameters:

NOT, BUFFER gates  : take a single arg
XOR, XNOR gates    : take two args
AND, OR, NAND, NOR gates : takes *args
"""

def NOT(arg):
    return (not arg);

def BUFFER(arg):
    return arg

def AND(*args):
    return (False not in args)

def NAND(*args):
    return (False in args)

def OR(*args):
    return (True in args);

def NOR(*arg):
    return (not True in arg)

def XOR(argA, argB):
    return (argA != argB)

def XNOR(argA, argB):
    return (argA == argB)
