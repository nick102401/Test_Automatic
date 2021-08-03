# -*-coding:utf-8-*-
import json
import time
from datetime import datetime, timedelta

from FastApi.common.log import Logger

log = Logger().logger


def get_value_from_resp(in_dict, target_key, locate_key="", locate_value=".*"):
    """
    根据已知K,V获取另一个K对应的V
    :param in_dict:
    :param target_key:
    :param locate_key:
    :param locate_value:
    :return:
    """
    ret = recursion_search(in_dict, target_key, locate_key, locate_value)
    if ret:
        return ret
    else:
        log.error("get_value_from_resp failed!")
        return False


def recursion_search(in_dict, target_key, locate_key="", locate_value=""):
    """
    递归：根据已知K,V获取另一个K对应的V
    :param in_dict:
    :param target_key:
    :param locate_key:
    :param locate_value:
    :return:
    """
    if isinstance(in_dict, dict):
        for k, v in in_dict.items():
            if isinstance(v, dict):
                ret = recursion_search(v, target_key, locate_key, locate_value)
                if ret:
                    return ret
            elif isinstance(v, list):
                for item in v:
                    ret = recursion_search(item, target_key, locate_key, locate_value)
                    if ret:
                        return ret
            else:
                if locate_key:
                    if k == locate_key and v == locate_value:
                        return in_dict[target_key]
                elif k == target_key:
                    return v


def bjs_to_utc(bjs_time):
    """
    北京时间转格林时间
    :param bjs_time:
    :return:
    """
    utc_format = "%Y-%m-%dT%H:%M:%S"
    bjs_format = "%Y-%m-%d %H:%M:%S"
    bjs_time = datetime.strptime(bjs_time, bjs_format)
    # 北京时间-8小时变为格林威治时间
    utc_time = bjs_time - timedelta(hours=8)
    utc_time = utc_time.strftime(utc_format)
    return utc_time


def utc_to_bjs(utc_time):
    """
    格林时间转北京时间
    :param utc_time:
    :return:
    """
    utc_format = "%Y-%m-%dT%H:%M:%S.%f"
    bjs_format = "%Y-%m-%d %H:%M:%S"
    utc_time = datetime.strptime(utc_time, utc_format)
    # 格林威治时间+8小时变为北京时间
    bjs_time = utc_time + timedelta(hours=8)
    bjs_time = bjs_time.strftime(bjs_format)
    return bjs_time


def utc_to_gmt(utc_time, utc_fmt="%Y-%m-%d %H:%M:%S", gmt_fmt="%a %b %d %Y %H:%M:%S GMT+0800"):
    """
    UTC格式时间转GMT格式时间
    :param utc_time:
    :param utc_fmt:
    :param gmt_fmt:
    :return:
    """
    return time.strftime(gmt_fmt, time.strptime(utc_time, utc_fmt))


if __name__ == '__main__':
    pass
    resp = {'content': {'code': 0, 'msg': 'success', 'data': {'list': [
        {'projectId': 'P-a6686a9fe06644efbd142b3fba9a20c2', 'projectName': 'P2', 'description': '', 'logo': None,
         'creatorId': 'd77aee4d5fda46b296bd14e34586ca27', 'creatorName': None, 'sprintIndex': 0, 'archive': 0,
         'disabled': None, 'startTime': '2021-08-01T16:00:00.000+00:00', 'endTime': '2021-08-01T16:00:00.000+00:00',
         'assessFlag': '0'},
        {'projectId': 'P-0c2ea4e3a6b845e58f36dab0da514706', 'projectName': 'P1', 'description': '55555', 'logo': None,
         'creatorId': 'd77aee4d5fda46b296bd14e34586ca27', 'creatorName': None, 'sprintIndex': 0, 'archive': 0,
         'disabled': None, 'startTime': '2021-08-11T16:00:00.000+00:00', 'endTime': '2021-08-30T16:00:00.000+00:00',
         'assessFlag': '0'},
        {'projectId': 'P-5b2da47b5bff413da88ba519933b8841', 'projectName': '项目三', 'description': '', 'logo': None,
         'creatorId': 'd77aee4d5fda46b296bd14e34586ca27', 'creatorName': None, 'sprintIndex': 0, 'archive': 0,
         'disabled': None, 'startTime': '2021-07-29T16:00:00.000+00:00', 'endTime': '2021-08-30T16:00:00.000+00:00',
         'assessFlag': '1'},
        {'projectId': 'P-73b7892b837b46e5a498638a90b8c4a4', 'projectName': '项目一', 'description': None, 'logo': None,
         'creatorId': '7d8585db0ef641d186fa98a8e105ecfa', 'creatorName': None, 'sprintIndex': 0, 'archive': 0,
         'disabled': None, 'startTime': '2021-05-31T16:00:00.000+00:00', 'endTime': '2021-08-31T16:00:00.000+00:00',
         'assessFlag': '1'}], 'meta': {'total': 4, 'perPage': 11, 'creators': [
        {'userId': 'd77aee4d5fda46b296bd14e34586ca27', 'operatorNo': '18122222222', 'userName': 'PM', 'pwd': None,
         'realName': '18122222222', 'mobile': '18122222222', 'email': None, 'address': None, 'status': '1',
         'creatorId': None, 'loginAt': None, 'loginAmount': None, 'systemId': None, 'token': None, 'tokenExpire': None,
         'createdAt': None, 'updatedAt': None, 'isSuperAdmin': 0, 'wechatId': None, 'alipayId': None},
        {'userId': '7d8585db0ef641d186fa98a8e105ecfa', 'operatorNo': '18111111111', 'userName': '开发', 'pwd': None,
         'realName': '18111111111', 'mobile': '18111111111', 'email': None, 'address': None, 'status': '1',
         'creatorId': None, 'loginAt': None, 'loginAmount': None, 'systemId': None, 'token': None, 'tokenExpire': None,
         'createdAt': None, 'updatedAt': None, 'isSuperAdmin': 0, 'wechatId': None, 'alipayId': None}], 'page': 1}}},
            'retCode': 200}
    print(type(resp['content']))
    print(get_value_from_resp(resp['content'], 'userId', 'operatorNo', '18122222222'))
