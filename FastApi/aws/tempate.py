from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.common.helper import get_value_from_resp
from FastApi.conf import env


class Temps(Common):
    """
    模板操作类
    """

    def __init__(self):
        super(Temps, self).__init__()

    @staticmethod
    def query_template_id_by_name(templateName='', userName=env.USERNAME_PM):
        """
        根据模板名称查询模板ID
        :param templateName:
        :param userName: 默认查询PM角色下模板
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/system/temps'

        resp = req_exec(method, url, username=userName)
        if templateName:
            return get_value_from_resp(resp['content'], 'tempId', 'tempName', templateName)
        return resp


if __name__ == '__main__':
    temp = Temps()
    print(temp.query_template_id_by_name(templateName='基本模板'))
