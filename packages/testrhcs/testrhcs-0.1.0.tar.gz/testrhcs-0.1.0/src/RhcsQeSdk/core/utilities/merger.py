def merge_dicts(dict1, dict2):
    """
    Returns dict1 by recursively merging dict2 into dict1
    Args:
        dict1 (dict):     The dictionary corressponding to <deploy_cluster> test.
        dict2 (dict):     The dictionary corressponding to test scenarios of different component in ceph.
    Returns:
        Dict -> dictionary after merging dict1 with dict2
    """
    if isinstance(dict1, list) and isinstance(dict2, list):
        res = []
        extended_list = dict1 + dict2
        dict1 = [x for x in extended_list if x not in res]
        return dict1
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for k in dict2:
        if k in dict1:
            dict1[k] = merge_dicts(dict1[k], dict2[k])
        else:
            dict1[k] = dict2[k]
    return dict1
