def shrink_dict(target_dict, compare_dict):
    """
    :param target_dict:
    :param compare_dict:
    :return:
    """
    return {key: target_dict[key] for key in compare_dict}


def sync_key(target_dict, compare_dict):
    """
    :param target_dict:
    :param compare_dict:
    :return:
    """
    return {key: target_dict[key] for key in compare_dict}


if __name__ == '__main__':
    a = dict(a=1, b=2, c=3)
    b = dict(c=1)

    print(sync_key(a, b))
