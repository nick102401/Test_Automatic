import json

from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.common.helper import get_value_from_resp
from FastApi.conf import env


class ProjectsMgt(Common):
    def __init__(self):
        super().__init__()

    def query_project(self):
        """
        查询当前用户名下所有项目
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/user/projects?currentPage={0}&perPage={1}&type=filter'.format(self.currentPage,
                                                                                                 self.perPage)
        resp = req_exec(method, url, username=env.USERNAME_PM)
        return resp

    def query_project_id_by_name(self, projectName):
        resp = self.query_project()
        return get_value_from_resp(resp['content'], 'projectName', projectName, 'projectId')


if __name__ == '__main__':
    pv = ProjectsMgt()
    # pv.query_project()
    print(pv.query_project_id_by_name('P1'))
