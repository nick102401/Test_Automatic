from FastApi.aws.project import Project
from FastApi.common.base_api import req_exec
from FastApi.common.common import Common
from FastApi.conf import env


class Recruitment(Common):
    """
    项目招聘
    """

    def __init__(self):
        super(Recruitment, self).__init__()
        self.perPage = 100
        self.project = Project()

    def query_project_recruitment(self, postType=0, userName=env.USERNAME_PG):
        """
        查询项目招聘信息
        :param postType: 职位类型:  0:全部类型
                                  1:Java后端
                                  2:Web前端
                                  3:手机前端
                                  4:小程序
                                  5:UI
                                  6:测试
        :param userName: 默认为职能人员
        :return:
        """
        method = 'GET'
        url = '/api/task/case/task/project/recruit/?'
        if postType != 0:
            url += 'postType=' + str(postType) + '&'

        url += 'currentPage={0}&perPage={1}'.format(self.currentPage, self.perPage)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_recruitment_by_project(self, projectName, userName=env.USERNAME_PG):
        """
        查询项目招聘信息
        :param projectName: 项目名称
        :param userName: 默认为职能人员
        :return:
        """
        # 获取项目ID
        projectId = self.project.query_project_id_by_name(projectName, userName=userName)

        method = 'GET'
        url = '/api/task/case/task/project/{0}/project/recruit/'.format(projectId)

        resp = req_exec(method, url, username=userName)
        return resp

    def query_position_info_by_name(self, postName, projectName, userName=env.USERNAME_PG):
        """
        根据职位名称查询职位信息
        :param postName: 职位名称
        :param projectName: 项目名称
        :param userName: 默认为职能人员
        :return:
        """
        resp = self.query_recruitment_by_project(projectName=projectName, userName=userName)
        projectRecruitList = resp['content']['data']['item']['projectRecruit']
        if projectRecruitList:
            for projectRecruit in projectRecruitList:
                if projectRecruit['postName'] == postName:
                    return projectRecruit
            else:
                raise Exception('暂无该职位招聘信息,请核实后操作')
        else:
            raise Exception('暂无该项目招聘信息,请核实后操作')

    def query_position_id_by_name(self, postName, projectName, userName=env.USERNAME_PG):
        """
        根据职位名称查询职位ID
        :param postName: 职位名称
        :param projectName: 项目名称
        :param userName: 默认为职能人员
        :return:
        """
        resp = self.query_recruitment_by_project(projectName=projectName, userName=userName)
        projectRecruitList = resp['content']['data']['item']['projectRecruit']
        if projectRecruitList:
            for projectRecruit in projectRecruitList:
                if projectRecruit['postName'] == postName:
                    return projectRecruit['recruitId']
            else:
                raise Exception('暂无该职位招聘信息,请核实后操作')
        else:
            raise Exception('暂无该项目招聘信息,请核实后操作')

    def apply_position(self, postName, projectName, applyUserDescription='', userName=env.USERNAME_PG):
        """
        申请职位
        :param postName: 职位名称
        :param projectName: 项目名称
        :param applyUserDescription: 申请描述
        :param userName: 默认为职能人员
        :return:
        """
        # 获取项目ID
        positionInfo = self.query_position_info_by_name(postName, projectName=projectName, userName=userName)

        if positionInfo:
            # 获取项目ID
            projectId = positionInfo['projectId']
            # 获取角色ID
            proRoleId = positionInfo['proRoleId']
            # 获取职位ID
            recruitId = positionInfo['recruitId']

            method = 'POST'
            data = {
                'applyStatus': 0,
                'applyUserDescription': applyUserDescription,
                'applyUserId': proRoleId,
                'projectId': projectId,
                'recruitId': recruitId,
                'applyType': 1
            }
            url = '/api/task/case/task/projects/apply'

            resp = req_exec(method, url, data=data, username=userName)
            return resp
        else:
            raise Exception('申请职位不存在,请核实后操作')


if __name__ == '__main__':
    rec = Recruitment()
    # rec.query_project_recruitment(postType=4)
    # rec.query_recruitment_by_project(projectName='中文名称项目111')
    # rec.apply_position(postName='中文测试', projectName='中文名称项目111')
