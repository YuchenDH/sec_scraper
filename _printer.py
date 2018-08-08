def print_dict(d, indent):
    if not isinstance(d, dict):
        print(d)
    print('{')
    for k, v in d.items():
        for i in range((indent+1) * 2):
            print(' ',)
        print (k + ':',)
        if isinstance(v, dict):
            print_dict(v, indent+1)
        elif isinstance(v, list):
            print_list(v, indent+1)
        else:
            print(repr(v) + ',')
    for i in range(indent * 2):
        print(' ',)
    print('}')


def print_list(l, indent):
    if not isinstance(l, list):
        print(l)
    print('[')
    for v in l:
        for i in range((indent+1) * 2):
            print(' ',)
        if isinstance(v, dict):
            print_dict(v, indent+1)
        elif isinstance(v, list):
            print_list(v, indent+1)
        else:
            print(repr(v) + ',')
    for i in range(indent * 2):
        print (' ',)
    print(']')
