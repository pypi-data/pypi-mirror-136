from circuits_py.state import State, logic_gate

def divide(source: State, *paths: callable):
    """
    divide a source path into paths

    :param source: State obj path to be divided
    :param paths: path functions which take source param
    """
    if (type(source) != State):
        raise ValueError(f"given source is not a State object \
        \n divide(source, *paths) \
        \n        ^^^^^ source must be a State object")
    for idx, path in enumerate(paths):
        if (not callable(path)):
            raise ValueError(f"given path at index {idx} is not callable \
            \n divide(source, *paths) \
            \n                 ^^^^^ paths have to be callable functions which take 'source' parameter \
            \n context: \
            \n divide() calls each path function passing the source as arg")
        path(source)

def combine(*sources: State, Logic: callable=logic_gate(lambda *args: False)):
    """
    combine two or more paths to a logic gate

    combine(
        State(b).NOT().AND(a),  # source
        State(a).NOT().AND(b),  # source
            Logic=logic.OR      # Logic function
    )

    :param *sources: State() objects, from the paths to combine
    :param Logic: a function which takes *sources parameters and returns a `bool` output
                  (the function should use the logic_gate decorator)
    """
    srl = []
    for idx, sr in enumerate(sources):
        if (type(sr) != State):
            raise ValueError(f"given source at index {idx} is not a State object \
            \n combine(*sources, Logic=logic) \
            \n          ^^^^^ sources must be State objects\n")
        srl.append(sr.get_output())

    if (not callable(Logic)):
        raise ValueError(f"given Logic function is not callable \
            \n combine(*sources, Logic=logic) \
            \n                         ^^^^^ Logic function must be callable\n")
    return Logic(*srl)
