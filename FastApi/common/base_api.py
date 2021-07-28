import json

import requests
import warnings

from FastApi.common.log import Logger

warnings.filterwarnings('ignore')
log = Logger().logger

header = {'Content-Type': 'application/json;charset=UTF-8'}


class ApiDriver:
    def __init__(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def get_token(self):
        pass

    @staticmethod
    def get(url):
        response = requests.get(url=url, verify=False)
        return dict({'content': response.text, 'retCode': response.status_code})

    @staticmethod
    def post(url, data, headers):
        response = requests.post(url=url, data=data, headers=headers, verify=False)
        return dict({'content': response.text, 'retCode': response.status_code})

    @staticmethod
    def put(url, data, headers):
        response = requests.put(url=url, data=data, headers=headers, verify=False)
        return dict({'content': response.text, 'retCode': response.status_code})

    @staticmethod
    def delete(url, data, headers):
        response = requests.delete(url=url, data=data, headers=headers, verify=False)
        return dict({'content': response.text, 'retCode': response.status_code})


def req_exec(method, url, data, headers=None):
    # 默认请求头参数
    if headers is None:
        headers = header
    # 默认返回
    response = None

    if method == 'GET':
        response = ApiDriver.get(url)
    elif method == 'POST':
        response = ApiDriver.post(url, data, headers=headers)
    elif method == 'PUT':
        response = ApiDriver.put(url, data, headers=headers)
    elif method == 'DELETE':
        response = ApiDriver.delete(url, data, headers=headers)

    # 日志打印
    log.info('[Method]---------------' + method + '---------------')
    log.info('[URL]' + url)
    log.info('[Response]' + str(response))
    return response


if __name__ == '__main__':
    driver = ApiDriver()
    resp = req_exec(method='POST',
                    url='http://192.168.96.127:9999/api/sys/login',
                    data='{"param_a":"YWRtaW4=","param_p":"31e7d8e0dd5be7db38333cce7b342c5d"}')
    print(json.loads(resp['content'])['data']['token'])
