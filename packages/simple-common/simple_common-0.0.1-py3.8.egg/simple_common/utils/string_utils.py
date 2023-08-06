def str_contain_some(some_str, *args):
    for target in args:
        if some_str.find(target) > 0:
            return True
    return False
