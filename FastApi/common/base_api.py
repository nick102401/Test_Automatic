import json

import requests
import warnings
from requests_toolbelt import MultipartEncoder

from FastApi.common.data_handle import MultipartFormData
from FastApi.common.log import Logger
from FastApi.conf import env

warnings.filterwarnings('ignore')
log = Logger().logger

header = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/92.0.4515.107 Safari/537.36 '
}


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
    def patch(url, data, headers=None):
        response = requests.patch(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})

    @staticmethod
    def put(url, data, headers=None):
        response = requests.put(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})

    @staticmethod
    def delete(url, data, headers=None):
        response = requests.delete(url=url, data=data, headers=headers, verify=False)
        return dict({'content': json.loads(response.text), 'retCode': response.status_code})


def req_exec(method, url, data=None, headers=None, username=env.USERNAME_PG, password=env.USER_PWD):
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

    # form data数据处理
    print_data = data
    if method != 'GET':
        headers['Content-Type'] = 'multipart/form-data; boundary=----WebKitFormBoundaryE5rQMWaGDbOsS38U'
        mfd = MultipartFormData()
        data = mfd.format(reqData=data, headers=headers)
        # 中文参数统一处理
        data = data.encode('utf-8')

    # url拼接
    if not url.startswith('/'):
        url = '/' + url
    url = 'http://' + env.HOST + ':' + env.PORT + url

    # 默认返回
    response = None
    if method == 'GET':
        response = api_driver.get(url, headers=headers)
    elif method == 'POST':
        response = api_driver.post(url, data, headers=headers)
    elif method == 'PATCH':
        response = api_driver.patch(url, data, headers=headers)
    elif method == 'PUT':
        response = api_driver.put(url, data, headers=headers)
    elif method == 'DELETE':
        response = api_driver.delete(url, data, headers=headers)

    # 日志打印
    log.info('[' + method + ']:' + url)
    if method != 'GET':
        log.info('[DATA]:' + str(print_data))
    log.info('[RESP]:' + str(response))
    return response


if __name__ == '__main__':
    driver = ApiDriver(env.USERNAME_PG, env.USER_PWD)
    # print(driver.login())
    # print(driver.get_token())
    # print(is_login())
    # resp = req_exec(method='POST',
    #                 url='http://192.168.96.127:9999/api/sys/login',
    #                 data='{"param_a":"YWRtaW4=","param_p":"31e7d8e0dd5be7db38333cce7b342c5d"}')
    # print(json.loads(resp['content'])['data']['token'])
