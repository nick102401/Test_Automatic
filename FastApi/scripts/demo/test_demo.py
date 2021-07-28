import allure
import requests

from FastApi.common.logger import Logger

log = Logger().logger
session = requests.session()


def setup():
    log.info('-----这是测试用例预制步骤-----')


@allure.feature('特性名称')
@allure.story('需求名称')
@allure.title('用例名称')
def test_step():
    log.info('-----这是测试用例执行步骤-----')


def teardown():
    log.info('-----这是测试用例清理环境操作-----')
