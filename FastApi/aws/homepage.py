from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.conf import env


class PersonalHomepage(Common):
    def __init__(self):
        super(PersonalHomepage, self).__init__()

    def query_my_approvals(self, userName=env.USERNAME_PMO):
        """
        查询我的所有审批
        :param userName: 默认PMO角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/approve/current?currentPage={0}&perPage={1}'.format(self.currentPage,
                                                                                                self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_pending_approvals(self, userName=env.USERNAME_PMO):
        """
        查询我的待审批
        :param userName: 默认PMO角色
        :return:
        """
        pendingApprovals = []
        resp = self.query_my_approvals(userName=userName)
        for approval in resp['content']['data']['list']:
            if approval['approveStatus'] == '0':
                pendingApprovals.append(approval)
        return pendingApprovals


if __name__ == '__main__':
    ph = PersonalHomepage()
    ph.query_my_approvals()
