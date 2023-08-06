import math
from functools import reduce

__all__ = ['tune_upstream_weight', 'tune_upstream_ratio']


def tune_upstream_weight(traffic_info):
    traffic = traffic_info.copy(deep=True)
    item_list = traffic.item_list()

    convert_list = list(filter(lambda x: x.ratio and x.ratio > 0, item_list))

    zero_list = [item for item in item_list if item not in convert_list]

    if len(convert_list) <= 1:
        for name, value in traffic.items():
            if value.ratio == 0:
                value.weight = 0
            else:
                value.ratio = 100
                value.weight = 10

        return traffic

    base_category = convert_list[0]

    contrast_category_list = convert_list[1:]

    calc_list = []

    for target_platform in contrast_category_list:
        calc_tuple = (
            base_category.ratio * target_platform.count,
            target_platform.ratio * base_category.count,
        )

        calc_list.append(calc_tuple)

    def get_min_ab(pre, current):
        return pre[0] * current[0] // math.gcd(pre[0], current[0]), current[1]

    max_x = reduce(get_min_ab, calc_list)[0]

    def extend_to_max(t):
        return max_x, max_x // t[0] * t[1]

    calc_list = list(map(extend_to_max, calc_list))

    base_category.weight = calc_list[0][0]

    index = 0
    for target_platform in contrast_category_list:
        target_platform.weight = calc_list[index][1]
        index += 1

    def get_weight_list(v):
        return v.weight

    weight_list = list(map(get_weight_list, convert_list))

    gcd = get_gcd(*weight_list)

    for item in convert_list:
        item.weight = item.weight // gcd

    for item in zero_list:
        item.weight = 0

    return traffic


def get_gcd(*args):
    res = 1
    for i in range(min(args), 0, -1):
        flag = False
        for target in args:
            if target % i != 0:
                flag = True
                break

        if not flag:
            res = i
            break

    return res


def tune_upstream_ratio(traffic_info):
    # use math.floor(), so ratio < really ratio
    traffic = traffic_info.copy(deep=True)
    total_weight = 0
    platform_weight_count = dict()

    for name, item in traffic.items():
        total_weight += item.weight * item.count
        platform_weight_count[name] = item.weight * item.count
    for name, value in traffic.items():
        value.ratio = math.floor(platform_weight_count[name] / total_weight * 100)
    return traffic
