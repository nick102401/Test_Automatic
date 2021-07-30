# -*-coding:utf-8-*-

def get_value_from_resp(in_dict, key, value, target_key):
    """
    根据一对K,V以及另一个K获取另一个V
    :param in_dict:
    :param key:
    :param value:
    :param target_key:
    :return:
    """
    for k, v in in_dict.items():
        if isinstance(v, dict):
            return get_value_from_resp(v, key, value, target_key)
        elif isinstance(v, list):
            return get_list_value(v, key, value, target_key)

        # 如果当前键值与输入键值相等, 并且判断是否要筛选
        if key == k and value == v and not isinstance(v, dict):
            target_value = in_dict[target_key]
            return target_value


def get_list_value(in_list, key, value, target_key):
    for ele in in_list:
        if isinstance(ele, list):
            return get_list_value(ele, key, value, target_key)
        elif isinstance(ele, dict):
            return get_value_from_resp(ele, key, value, target_key)
