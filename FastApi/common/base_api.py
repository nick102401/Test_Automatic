import json

import requests
import warnings
from requests_toolbelt import MultipartEncoder
from FastApi.common.log import Logger
from FastApi.conf import env

warnings.filterwarnings('ignore')
log = Logger().logger

header = {'Content-Type': 'application/json;charset=UTF-8'}


class ApiDriver:
    """
    登录
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        m = MultipartEncoder(fields={'operatorNo': self.username,
                                     'userPwd': self.password,
                                     'validCode': ''})
        url = '/api/user/sign/in'
        url = 'http://' + env.HOST + ':' + env.PORT + url
        response = requests.post(url=url, data=m, headers={'Content-Type': m.content_type})
        return dict({'content': response.text, 'retCode': response.status_code})

    def logout(self):
        pass

    def get_token(self):
        response = self.login()
        token = json.loads(response['content'])['data']['meta']['token']
        return token

    @staticmethod
    def get(url, headers=None):
        response = requests.get(url=url, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})

    @staticmethod
    def post(url, data, headers=None):
        response = requests.post(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})

    @staticmethod
    def put(url, data, headers=None):
        response = requests.put(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})

    @staticmethod
    def delete(url, data, headers=None):
        response = requests.delete(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})


def req_exec(method, url, data=None, headers=None, username=env.USERNAME, password=env.PASSWORD):
    """
    接口执行
    :param method:接口请求方式
    :param url: 接口url
    :param data:接口入参
    :param headers: 接口请求头
    :param username: 登录账号
    :param password: 登录密码
    :return:
    """
    # 获取token
    api_driver = ApiDriver(username=username, password=password)
    token = api_driver.get_token()
    header['token'] = token

    # 默认请求头参数
    if headers is None:
        headers = header

    # 默认返回
    response = None

    # form data数据处理
    if data:
        m = MultipartEncoder(fields=data)
        header['Content-Type'] = m.content_type

    # url拼接
    if not url.startswith('/'):
        url = '/' + url
    url = 'http://' + env.HOST + ':' + env.PORT + url

    if method == 'GET':
        response = api_driver.get(url, headers=headers)
    elif method == 'POST':
        response = api_driver.post(url, data, headers=headers)
    elif method == 'PUT':
        response = api_driver.put(url, data, headers=headers)
    elif method == 'DELETE':
        response = api_driver.delete(url, data, headers=headers)

    # 日志打印
    log.info('[' + method + ']:' + url)
    if method != 'GET':
        log.info('[Data]:' + str(data))
    log.info('[Resp]:' + str(response))
    return response


if __name__ == '__main__':
    driver = ApiDriver(env.USERNAME, env.PASSWORD)
    # print(driver.login())
    print(driver.get_token())
    # resp = req_exec(method='POST',
    #                 url='http://192.168.96.127:9999/api/sys/login',
    #                 data='{"param_a":"YWRtaW4=","param_p":"31e7d8e0dd5be7db38333cce7b342c5d"}')
    # print(json.loads(resp['content'])['data']['token'])
