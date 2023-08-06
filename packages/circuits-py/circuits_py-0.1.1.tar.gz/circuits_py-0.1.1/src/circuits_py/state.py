from circuits_py import logic
import functools

states_allowed = set([1, 0, False, True])

class InvalidStateException(Exception):
    def __init__(self, message, given={}, valid={0, 1}):
        self.message = message
        self.given = given
        self.valid = valid
    def __str__(self):
        return str(f"{self.message} \
                    \n  valid={self.valid} \
                    \n  given={self.given}")

def is_valid_state(*args):
    """returns True if *args contain only [0, 1, True, False] values"""
    for arg in args:
        if (type(arg) not in {int, bool}):
            return False
    return (set(args).issubset(states_allowed))

def logic_gate(l_func=None, ignore_self_arg=False):
    """
    :param ignore_self_arg: pass True if called from a method inside a class
    """
    def logic_gate_dec(logic_func: callable):
        @functools.wraps(logic_func)
        def inner(*inputs, **kwargs):
            """
            decorator

            creates a new State() initialized to the output of the passed function
            checks if the given *args and returned output from the function are valid state values

            :param logic_func: a function which takes input parameters and returns a bool result
            :param *inputs: True or False values
            :return: State() object initialized to the output of the logic_func
            """
            given_args = inputs
            if (ignore_self_arg):
                given_args = inputs[1:]
            if (not is_valid_state(*given_args)):
                s = ""
                if (len(given_args) > 1):
                    s = "s"
                raise InvalidStateException(f"given arg{s} to '{logic_func.__name__}()' contains invalid state", given={given_args})
            output = logic_func(*inputs)
            if (not is_valid_state(output)):
                raise InvalidStateException(f"given logic function '{logic_func.__name__}()' returned a invalid State", given={output})
            return State(output)
        return inner
    return logic_gate_dec(l_func) if callable(l_func) else logic_gate_dec

class State:
    """State object, can be initialized to [0, 1, True, False] values"""
    def __init__(self, state):
        if (not is_valid_state(state)):
            raise InvalidStateException(f"given state is invalid", given={state})
        self.state = state
        self.handlers = []

    @logic_gate(ignore_self_arg=True)
    def AND(self, *args):
        return logic.AND(self.state, *args)

    @logic_gate(ignore_self_arg=True)
    def BUFFER(self):
        return logic.BUFFER(self.state)

    @logic_gate(ignore_self_arg=True)
    def NAND(self, *args):
        return logic.NAND(self.state, *args)

    @logic_gate(ignore_self_arg=True)
    def OR(self, *args):
        return logic.OR(self.state, *args)

    @logic_gate(ignore_self_arg=True)
    def NOR(self, *arg):
        return logic.NOR(self.state, *arg)

    @logic_gate(ignore_self_arg=True)
    def NOT(self):
        return logic.NOT(self.state)

    @logic_gate(ignore_self_arg=True)
    def XOR(self, arg):
        return logic.XOR(self.state, arg)

    @logic_gate(ignore_self_arg=True)
    def XNOR(self, arg):
        return logic.XNOR(self.state, arg)

    def to_int(self):
        self.state = int(self.state)
        return self

    def to_bool(self):
        self.state = bool(self.state)
        return self

    def get_output(self):
        return self.state

    def add_output_handler(self, *output_handlers: callable):
        for out_handler in output_handlers:
            self.handlers.append(out_handler)
        return self

    def call_handlers(self):
        for handler in self.handlers:
            handler(self.state)
        return self
