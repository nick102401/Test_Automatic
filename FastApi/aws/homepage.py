from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.conf import env


class PersonalHomepage(Common):
    """
    个人主页
    """

    def __init__(self):
        super(PersonalHomepage, self).__init__()
        self.perPage = 100

    @staticmethod
    def query_participant_project(userName=env.USERNAME_PM):
        """
        查询参与的项目信息
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/mine/tasks/summary'

        resp = req_exec(method, url, username=userName)
        return resp

    def query_my_applications(self, userName=env.USERNAME_PM):
        """
        查询我的所有申请
        :param userName: 默认为PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/projects/apply?currentPage={0}&perPage={1}'.format(self.currentPage,
                                                                                      self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_pending_applications(self, userName=env.USERNAME_PM):
        """
        查询我的待审批申请
        :param userName: 默认为PM角色
        :return:
        """
        pendingApplications = []
        resp = self.query_my_applications(userName=userName)
        applicationList = resp['content']['data']['list']
        if applicationList:
            for application in applicationList:
                if application['applyStatus'] == '0':
                    pendingApplications.append(application)
            return pendingApplications
        else:
            raise Exception('暂无我的申请,请核实后操作')

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
        approvalList = resp['content']['data']['list']
        if approvalList:
            for approval in approvalList:
                if approval['approveStatus'] == '0':
                    pendingApprovals.append(approval)
            return pendingApprovals
        else:
            raise Exception('暂无我的审批,请核实后操作')

    def query_assessment_content(self, userName=env.USERNAME_PM):
        """
        查询考核内容
        :param userName: 默认PM角色
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/assessNotice/manager?currentPage={0}&perPage={1}'.format(self.currentPage,
                                                                                            self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp


if __name__ == '__main__':
    ph = PersonalHomepage()
    # ph.query_participant_project()
    # ph.query_my_approvals()
