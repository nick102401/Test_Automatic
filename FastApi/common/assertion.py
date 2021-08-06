"""
封装Assert方法

"""
import json
import traceback

from FastApi.common.log import Logger


class Assertions:
    def __init__(self):
        pass

    @staticmethod
    def assert_status_code(status_code, expected_code):
        """
        验证response状态码
        :param status_code:
        :param expected_code:
        :return:
        """
        try:
            assert status_code == expected_code
            return True

        except Exception:
            log_error(traceback.format_exc(), status_code, expected_code)
            raise

    @staticmethod
    def assert_single_item(single_item, expected_results):
        """
        验证response body中任意属性的值
        :param single_item:
        :param expected_results:
        :return:
        """
        try:
            assert single_item == expected_results
            return True

        except Exception:
            log_error(traceback.format_exc(), single_item, expected_results)
            raise

    @staticmethod
    def assert_in_text(body, expected_results):
        """
        验证response body中是否包含预期字符串
        :param body:
        :param expected_results:
        :return:
        """
        text = json.dumps(body, ensure_ascii=False)
        try:
            assert expected_results in text
            return True

        except Exception:
            log_error(traceback.format_exc(), text, expected_results)
            raise

    @staticmethod
    def assert_items(d_body, expected_results):
        """
        验证body里面的items是否符合期望
        需保证expected_results中是属性，在body中都能找到
        :param d_body: 一个dict/json
        :param expected_results: 一个dict/json
        :return:
        """
        for key, value in expected_results.items():
            try:
                if key in d_body.keys():
                    assert d_body[key] == value
                    return True
                else:
                    return False
            except Exception:
                log_error(traceback.format_exc(), d_body[key], value)
                raise

    @staticmethod
    def assert_time(actual_time, expected_time):
        """
        验证response body响应时间小于预期最大响应时间,单位：毫秒
        :param actual_time:
        :param expected_time:
        :return:
        """
        try:
            assert actual_time < expected_time
            return True

        except Exception:
            log_error(traceback.format_exc(), actual_time, expected_time)
            raise


def log_error(e, actual, expected):
    log = Logger(level='error').logger
    log.error(str(e))
    log.error('actual results is %s, expected results is %s ' % (actual, expected))
    # config = Config.Read_config()
    # config.set_conf('results', 'final_results', 'False')


if __name__ == '__main__':
    assertion = Assertions()
    assertion.assert_in_text('123456', '1237')
